from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
import tempfile
import os

from grid.jobs.models import (
    Job, JobAttachment, Language, Benefit, CancelReason, 
    InterviewStep, RecruiterApplication, JobNotes
)
from grid.clients.models import Client, Address, Industry, ClientUserProfile
from grid.recruiters.models import Recruiter, JobCategory, Agency
from grid.users.models import User
from grid.users.choices import Roles
from grid.site_settings.models import Country, State

User = get_user_model()


class JobModelTests(TestCase):
    """Test cases for Job model"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        # Create test country and state
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.state = State.objects.create(
            name='Test State', 
            country=self.country, 
            two_letter_code='TS'
        )
        
        # Create test industry
        self.industry = Industry.objects.create(name='Technology')
        
        # Create test client
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )
        
        # Create test address
        self.address = Address.objects.create(
            address1='123 Test St',
            city='Test City',
            state=self.state,
            country=self.country,
            client=self.client
        )
        
        # Create test job category
        self.job_category = JobCategory.objects.create(
            name='Software Development'
        )
        
        # Create test language
        self.language = Language.objects.create(name='English')
        
        # Create test benefit
        self.benefit = Benefit.objects.create(
            name='Health Insurance',
            description='Comprehensive health coverage'
        )
        
        # Job data
        self.job_data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for a senior software engineer...',
            'about_company': 'We are a tech company...',
            'must_haves': 'Python, Django, React',
            'nice_to_haves': 'AWS, Docker',
            'job_type': Job.JobType.REMOTE,
            'position_type': Job.PositionType.FULL_TIME,
            'visa_sponsorship': True,
            'salary_min': 80000,
            'salary_max': 120000,
            'expected_commission': 15000,
            'signup_bonus': 5000,
            'stocks_value': 10000,
            'commission_percentage': 20,
            'top_job': True,
            'book_of_business': False,
            'min_book_of_business': 0,
            'client': self.client,
            'location': self.address,
            'category': self.job_category,
            'posted_by': self.user,
        }

    def test_create_job(self):
        """Test creating a job"""
        job = Job.objects.create(**self.job_data)
        
        self.assertEqual(job.title, self.job_data['title'])
        self.assertEqual(job.client, self.client)
        self.assertEqual(job.status, Job.JobStatus.ACTIVE)
        self.assertEqual(job.no_of_roles, 1)  # Default value
        self.assertEqual(str(job), self.job_data['title'])

    def test_job_with_languages_and_benefits(self):
        """Test job with many-to-many relationships"""
        job = Job.objects.create(**self.job_data)
        job.languages.add(self.language)
        job.benefits.add(self.benefit)
        
        self.assertIn(self.language, job.get_languages())
        self.assertIn(self.benefit, job.get_benefits())

    def test_job_validation(self):
        """Test job field validations"""
        # Test negative expected commission
        invalid_data = self.job_data.copy()
        invalid_data['expected_commission'] = -1000
        
        with self.assertRaises(ValidationError):
            job = Job(**invalid_data)
            job.full_clean()

        # Test negative signup bonus
        invalid_data = self.job_data.copy()
        invalid_data['signup_bonus'] = -500
        
        with self.assertRaises(ValidationError):
            job = Job(**invalid_data)
            job.full_clean()

        # Test negative stocks value
        invalid_data = self.job_data.copy()
        invalid_data['stocks_value'] = -1000
        
        with self.assertRaises(ValidationError):
            job = Job(**invalid_data)
            job.full_clean()

    def test_job_status_choices(self):
        """Test job status choices"""
        job = Job.objects.create(**self.job_data)
        
        # Test different statuses
        for status_value, _ in Job.JobStatus.choices:
            job.status = status_value
            job.save()
            self.assertEqual(job.status, status_value)

    def test_job_type_choices(self):
        """Test job type choices"""
        job = Job.objects.create(**self.job_data)
        
        # Test different job types
        for job_type_value, _ in Job.JobType.choices:
            job.job_type = job_type_value
            job.save()
            self.assertEqual(job.job_type, job_type_value)

    def test_position_type_choices(self):
        """Test position type choices"""
        job = Job.objects.create(**self.job_data)
        
        # Test different position types
        for position_type_value, _ in Job.PositionType.choices:
            job.position_type = position_type_value
            job.save()
            self.assertEqual(job.position_type, position_type_value)

    def test_no_of_roles_validation(self):
        """Test number of roles validation"""
        # Test with 0 roles (should fail)
        invalid_data = self.job_data.copy()
        invalid_data['no_of_roles'] = 0
        
        with self.assertRaises(ValidationError):
            job = Job(**invalid_data)
            job.full_clean()

        # Test with negative roles (should fail)
        invalid_data['no_of_roles'] = -1
        
        with self.assertRaises(ValidationError):
            job = Job(**invalid_data)
            job.full_clean()

        # Test with valid roles
        valid_data = self.job_data.copy()
        valid_data['no_of_roles'] = 5
        
        job = Job(**valid_data)
        job.full_clean()  # Should not raise
        job.save()
        self.assertEqual(job.no_of_roles, 5)


class JobNotesTests(TestCase):
    """Test cases for JobNotes model"""

    def setUp(self):
        # Create minimal setup
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.industry = Industry.objects.create(name='Technology')
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )
        
        self.job = Job.objects.create(
            title='Test Job',
            salary_min=50000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )

    def test_create_job_notes(self):
        """Test creating job notes"""
        notes = JobNotes.objects.create(
            job=self.job,
            notes='This is a test note about the job.',
            user=self.user
        )
        
        self.assertEqual(notes.job, self.job)
        self.assertEqual(notes.user, self.user)
        self.assertEqual(notes.notes, 'This is a test note about the job.')
        self.assertEqual(str(notes), f'Notes for Job {self.job}')

    def test_multiple_notes_per_job(self):
        """Test multiple notes per job"""
        # Create multiple notes for the same job
        notes1 = JobNotes.objects.create(
            job=self.job,
            notes='First note',
            user=self.user
        )
        
        notes2 = JobNotes.objects.create(
            job=self.job,
            notes='Second note',
            user=self.user
        )
        
        job_notes = JobNotes.objects.filter(job=self.job)
        self.assertEqual(job_notes.count(), 2)


class JobAPITests(APITestCase):
    """Test cases for Job API endpoints"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='client@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        # Create minimal setup
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.state = State.objects.create(
            name='Test State', 
            country=self.country, 
            two_letter_code='TS'
        )
        self.industry = Industry.objects.create(name='Technology')
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )
        
        # Create client user profile
        self.client_profile = ClientUserProfile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            client=self.client
        )
        
        self.address = Address.objects.create(
            address1='123 Test St',
            city='Test City',
            state=self.state,
            country=self.country,
            client=self.client
        )
        
        self.job_category = JobCategory.objects.create(
            name='Software Development'
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)

    def test_create_job_api(self):
        """Test creating job via API"""
        url = '/api/jobs/'
        data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for a senior software engineer...',
            'salary_min': 80000,
            'salary_max': 120000,
            'job_type': Job.JobType.REMOTE,
            'position_type': Job.PositionType.FULL_TIME,
            'visa_sponsorship': True,
            'client': self.client.id,
            'location': self.address.id,
            'category': self.job_category.id,
            'min_book_of_business': 0
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify job was created
        job = Job.objects.get(title=data['title'])
        self.assertEqual(job.salary_min, data['salary_min'])
        self.assertEqual(job.posted_by, self.user)

    def test_list_jobs_api(self):
        """Test listing jobs via API"""
        # Create test jobs
        Job.objects.create(
            title='Job 1',
            salary_min=50000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        Job.objects.create(
            title='Job 2',
            salary_min=60000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        url = '/api/jobs/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_update_job_api(self):
        """Test updating job via API"""
        job = Job.objects.create(
            title='Original Title',
            salary_min=50000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        url = f'/api/jobs/{job.id}/'
        data = {
            'title': 'Updated Title',
            'salary_min': 70000
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify job was updated
        job.refresh_from_db()
        self.assertEqual(job.title, 'Updated Title')
        self.assertEqual(job.salary_min, 70000)

    def test_delete_job_api(self):
        """Test deleting job via API"""
        job = Job.objects.create(
            title='Job to Delete',
            salary_min=50000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        url = f'/api/jobs/{job.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Job.objects.filter(id=job.id).exists())

    def test_job_filtering_api(self):
        """Test job filtering via API"""
        # Create jobs with different attributes
        job1 = Job.objects.create(
            title='Remote Job',
            salary_min=80000,
            job_type=Job.JobType.REMOTE,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        job2 = Job.objects.create(
            title='On-site Job',
            salary_min=70000,
            job_type=Job.JobType.ON_SITE,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        # Filter by job type
        url = '/api/jobs/?job_type=1'  # Remote
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Remote Job')

    def test_job_search_api(self):
        """Test job search via API"""
        # Create jobs with different titles
        Job.objects.create(
            title='Python Developer',
            salary_min=80000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        Job.objects.create(
            title='Java Developer',
            salary_min=75000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        # Search for Python jobs
        url = '/api/jobs/?search=Python'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Developer')

    def test_job_permissions_api(self):
        """Test job permissions via API"""
        # Create job by another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        other_client = Client.objects.create(
            company_name='Other Company',
            industry=self.industry,
            country=self.country
        )
        
        job = Job.objects.create(
            title='Other User Job',
            salary_min=50000,
            client=other_client,
            posted_by=other_user,
            min_book_of_business=0
        )
        
        # Try to update job created by other user
        url = f'/api/jobs/{job.id}/'
        data = {'title': 'Hacked Title'}
        
        response = self.client.patch(url, data)
        # Should return 403 Forbidden or 404 Not Found depending on permissions
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class JobAttachmentAPITests(APITestCase):
    """Test cases for JobAttachment API endpoints"""

    def setUp(self):
        # Create test user and job
        self.user = User.objects.create_user(
            email='client@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.industry = Industry.objects.create(name='Technology')
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )
        
        self.job = Job.objects.create(
            title='Test Job',
            salary_min=50000,
            client=self.client,
            posted_by=self.user,
            min_book_of_business=0
        )
        
        self.client.force_authenticate(user=self.user)

    def test_upload_job_attachment_api(self):
        """Test uploading job attachment via API"""
        # Create test PDF file
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        test_file = SimpleUploadedFile(
            "test_document.pdf", 
            pdf_content, 
            content_type="application/pdf"
        )
        
        url = '/api/job-attachments/'
        data = {
            'file': test_file,
            'job': self.job.id
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify attachment was created
        attachment = JobAttachment.objects.get(job=self.job)
        self.assertEqual(attachment.uploaded_by, self.user)

    def test_invalid_file_upload_api(self):
        """Test uploading invalid file via API"""
        # Create test text file (should fail)
        invalid_file = SimpleUploadedFile(
            "test_document.txt", 
            b"This is not a PDF", 
            content_type="text/plain"
        )
        
        url = '/api/job-attachments/'
        data = {
            'file': invalid_file,
            'job': self.job.id
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_job_attachments_api(self):
        """Test listing job attachments via API"""
        # Create test attachments
        for i in range(3):
            pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
            test_file = SimpleUploadedFile(
                f"test_document_{i}.pdf", 
                pdf_content, 
                content_type="application/pdf"
            )
            
            JobAttachment.objects.create(
                file=test_file,
                uploaded_by=self.user,
                job=self.job
            )
        
        url = f'/api/job-attachments/?job={self.job.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)


class PerformanceTests(TestCase):
    """Performance tests for job operations"""

    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.industry = Industry.objects.create(name='Technology')
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )

    def test_bulk_job_creation_performance(self):
        """Test bulk job creation performance"""
        import time
        
        start_time = time.time()
        
        # Create 100 jobs
        jobs = []
        for i in range(100):
            job = Job(
                title=f'Job {i}',
                salary_min=50000 + i * 1000,
                client=self.client,
                posted_by=self.user,
                min_book_of_business=0
            )
            jobs.append(job)
        
        Job.objects.bulk_create(jobs)
        
        end_time = time.time()
        
        # Should complete within 2 seconds
        self.assertLess(end_time - start_time, 2)
        self.assertEqual(Job.objects.count(), 100)

    def test_job_query_optimization(self):
        """Test job query optimization"""
        # Create test jobs with related data
        for i in range(10):
            job = Job.objects.create(
                title=f'Job {i}',
                salary_min=50000,
                client=self.client,
                posted_by=self.user,
                min_book_of_business=0
            )
            
            # Create related data
            InterviewStep.objects.create(
                job=job,
                step_title=f'Step {i}',
                priority=1
            )
            
            JobNotes.objects.create(
                job=job,
                notes=f'Notes for job {i}',
                user=self.user
            )
        
        # Test optimized query
        from django.test import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Query with select_related and prefetch_related
            jobs = Job.objects.select_related('client', 'posted_by').prefetch_related(
                'interviewstep_set', 'jobnotes_set'
            ).all()
            
            # Force evaluation
            for job in jobs:
                job.client.company_name
                job.posted_by.email
                list(job.interviewstep_set.all())
                list(job.jobnotes_set.all())
            
            # Should use minimal queries
            query_count = len(connection.queries)
            self.assertLess(query_count, 10)


class IntegrationTests(APITestCase):
    """Integration tests for complete job workflows"""

    def setUp(self):
        # Create client user
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='testpass123',
            role=Roles.CLIENT
        )
        
        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            email='recruiter@example.com',
            password='testpass123',
            role=Roles.RECRUITER
        )
        
        # Create necessary objects
        self.country = Country.objects.create(name='Test Country', code='TC')
        self.state = State.objects.create(
            name='Test State', 
            country=self.country, 
            two_letter_code='TS'
        )
        self.industry = Industry.objects.create(name='Technology')
        
        self.client = Client.objects.create(
            company_name='Test Company',
            industry=self.industry,
            country=self.country
        )
        
        self.client_profile = ClientUserProfile.objects.create(
            user=self.client_user,
            first_name='John',
            last_name='Doe',
            client=self.client
        )
        
        self.agency = Agency.objects.create(
            name='Test Agency',
            country=self.country
        )
        
        self.recruiter = Recruiter.objects.create(
            user=self.recruiter_user,
            first_name='Jane',
            last_name='Smith',
            agency=self.agency
        )

    def test_complete_job_posting_workflow(self):
        """Test complete job posting workflow"""
        # 1. Client creates job
        self.client.force_authenticate(user=self.client_user)
        
        job_data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for a senior software engineer...',
            'salary_min': 80000,
            'salary_max': 120000,
            'job_type': Job.JobType.REMOTE,
            'position_type': Job.PositionType.FULL_TIME,
            'visa_sponsorship': True,
            'client': self.client.id,
            'min_book_of_business': 0
        }
        
        response = self.client.post('/api/jobs/', job_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        job_id = response.data['id']
        
        # 2. Add interview steps
        interview_data = {
            'job': job_id,
            'step_title': 'Technical Interview',
            'step_description': '1-hour technical assessment',
            'priority': 1
        }
        
        response = self.client.post('/api/interview-steps/', interview_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Upload job attachment
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        test_file = SimpleUploadedFile(
            "job_description.pdf", 
            pdf_content, 
            content_type="application/pdf"
        )
        
        attachment_data = {
            'file': test_file,
            'job': job_id
        }
        
        response = self.client.post('/api/job-attachments/', attachment_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. Recruiter applies to job
        self.client.force_authenticate(user=self.recruiter_user)
        
        application_data = {
            'job': job_id,
            'recruiter': self.recruiter.id
        }
        
        response = self.client.post('/api/recruiter-applications/', application_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 5. Client approves recruiter application
        self.client.force_authenticate(user=self.client_user)
        
        application_id = response.data['id']
        approval_data = {
            'status': RecruiterApplication.ApplicationStatus.APPROVED
        }
        
        response = self.client.patch(f'/api/recruiter-applications/{application_id}/', approval_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. Verify final state
        job = Job.objects.get(id=job_id)
        self.assertEqual(job.title, 'Senior Software Engineer')
        self.assertEqual(job.get_attachments().count(), 1)
        self.assertEqual(job.get_interview_steps().count(), 1)
        self.assertEqual(job.get_recruiters().count(), 1)

    def test_job_cancellation_workflow(self):
        """Test job cancellation workflow"""
        # Create job
        self.client.force_authenticate(user=self.client_user)
        
        job = Job.objects.create(
            title='Job to Cancel',
            salary_min=50000,
            client=self.client,
            posted_by=self.client_user,
            min_book_of_business=0
        )
        
        # Create cancel reason
        cancel_reason = CancelReason.objects.create(
            name='Budget Constraints',
            description='Not enough budget for this position'
        )
        
        # Cancel job
        cancel_data = {
            'status': Job.JobStatus.CANCELLED,
            'cancel_reason': cancel_reason.id
        }
        
        response = self.client.patch(f'/api/jobs/{job.id}/', cancel_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify cancellation
        job.refresh_from_db()
        self.assertEqual(job.status, Job.JobStatus.CANCELLED)
        self.assertEqual(job.cancel_reason, cancel_reason)
