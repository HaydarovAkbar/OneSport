from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import JobFilter
from .models import Job, JobAttachment, InterviewStep
from .serializers import (
    CreateJobSerializer, JobAttachmentSerializer, JobAttachmentDeleteSerializer, JobListSerializer, JobDetailSerializer,
    JobUpdateSerializer,
)
from ..core.pagination import CustomPagination
from ..core.permissions import IsClient


class JobAttachmentUploadView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = JobAttachmentSerializer

    def create(self, request, args, *kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uploaded_by=request.user)
        return Response({"uuid": serializer.data["uuid"]}, status=status.HTTP_201_CREATED)


class JobAttachmentDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobAttachmentDeleteSerializer
    queryset = JobAttachment.objects.all()
    lookup_field = 'uuid'

    def delete(self, request, args, *kwargs):
        try:
            self.destroy(request, args, *kwargs)
            return Response({"message": "Attachment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except JobAttachment.DoesNotExist:
            return Response({"error": "Attachment not found."}, status=status.HTTP_404_NOT_FOUND)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateJobSerializer
        elif self.action == 'list':
            return JobListSerializer
        elif self.action == 'retrieve':
            return JobDetailSerializer
        elif self.action == 'update':
            return JobUpdateSerializer
        return JobListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.all()

        if user.is_admin:
            return queryset

        elif user.is_recruiter:
            if hasattr(user, 'recruiter'):
                recruiter = user.recruiter
                queryset = queryset.filter(
                    (Q(location__state=recruiter.address.state) |
                     Q(location__country=recruiter.address.country)),
                    applications__recruiter=recruiter
                ).distinct()

        elif user.is_client:
            if hasattr(user, 'clientuserprofile'):
                return queryset.filter(client=user.clientuserprofile.client)
            else:
                raise PermissionDenied("Client profile not found for the user.")

        else:
            raise PermissionDenied("You do not have permission to view these jobs.")

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        client = getattr(user, "clientuserprofile", None).client if hasattr(user, "clientuserprofile") else None
        self.instance = serializer.save(posted_by=user, client=client)

    def create(self, request, args, *kwargs):
        response = super().create(request, args, *kwargs)
        job_data = self.instance.uuid
        message = "Job created successfully"
        response.data = {"message": message, "job_id": job_data}
        return response

    def perform_update(self, serializer):
        job = serializer.instance
        data = self.request.data

        new_benefits = data.get("benefits", [])
        if new_benefits:
            existing_benefits = set(job.benefits.values_list('uuid', flat=True))
            benefits_to_add = [benefit_uuid for benefit_uuid in new_benefits if benefit_uuid not in existing_benefits]
            job.benefits.add(*benefits_to_add)

        if not job.interviewstep_set.exists() and "interview_steps" in data:
            interview_steps = data["interview_steps"]
            for priority, step_title in enumerate(interview_steps, start=1):
                InterviewStep.objects.create(job=job, step_title=step_title, priority=priority)

        if "notes" in data:
            job.notes = data["notes"]
        if "about_company" in data:
            job.about_company = data["about_company"]
        if "nice_to_haves" in data:
            job.nice_to_haves = data["nice_to_haves"]

        serializer.save()
        message = "Job updated successfully"
        job_id = job.uuid
        response = {"message": message, "job_id": job_id}
        return response
