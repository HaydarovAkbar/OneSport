from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import FileField

from grid.clients.models import Address, Client
from grid.core.models import CoreModel
from grid.recruiters.models import JobCategory, Recruiter
from grid.site_settings.models import Country, Currency, State


def validate_file_extension(value):
    if not value.content_type == "application/pdf":
        raise ValidationError("Make sure the uploaded file is of type application/pdf")


def validate_expected_commission(value):
    if value < 0:
        raise ValidationError("Expected commission cannot be negative")
    return value


def validate_signup_bonus(value):
    if value < 0:
        raise ValidationError("Signup bonus cannot be negative")
    return value


def validate_stock_value(value):
    if value < 0:
        raise ValidationError("Stock value cannot be negative")
    return value


class Language(CoreModel):
    name = models.CharField(max_length=255)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Benefit(CoreModel):
    name = models.CharField(max_length=255)
    icon_name = models.CharField(max_length=255, null=True, blank=True)  # Optional icon field
    description = models.TextField(null=True, blank=True)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CancelReason(CoreModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(CoreModel):
    class JobStatus(models.IntegerChoices):
        ACTIVE = 0, "Active"
        CLOSED = 1, "Closed"
        PAUSED = 2, "Paused"
        CANCELLED = 3, "Cancelled"

    class PositionType(models.IntegerChoices):
        FULL_TIME = 0, "Full-time"
        PART_TIME = 1, "Part-time"
        CONTRACT = 2, "Contract"

    class JobType(models.IntegerChoices):
        ON_SITE = 0, "On-site"
        REMOTE = 1, "Remote"
        HYBRID = 2, "Hybrid"

    status = models.SmallIntegerField(choices=JobStatus.choices, default=JobStatus.ACTIVE)
    title = models.CharField(max_length=255)
    no_of_roles = models.IntegerField(
        null=False, blank=False, default=1, validators=[MinValueValidator(1, "No. of roles must be at least 1")]
    )
    description = models.TextField(null=True, blank=True)
    about_company = models.TextField(null=True, blank=True)
    must_haves = models.TextField(null=True, blank=True)
    nice_to_haves = models.TextField(null=True, blank=True)
    job_type = models.SmallIntegerField(choices=JobType.choices, default=JobType.ON_SITE)
    position_type = models.SmallIntegerField(choices=PositionType.choices, default=PositionType.FULL_TIME)
    visa_sponsorship = models.BooleanField(default=False)
    salary_min = models.IntegerField(null=False, blank=False)
    salary_max = models.IntegerField(null=True, blank=True)
    expected_commission = models.IntegerField(default=0, validators=[validate_expected_commission])
    signup_bonus = models.IntegerField(default=0, validators=[validate_signup_bonus])
    stocks_value = models.IntegerField(default=0, validators=[validate_stock_value])
    commission_percentage = models.SmallIntegerField(default=20)
    top_job = models.BooleanField(default=False)
    book_of_business = models.BooleanField(default=False)
    min_book_of_business = models.IntegerField()
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE)
    location = models.ForeignKey("clients.Address", on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey("recruiters.JobCategory", on_delete=models.SET_NULL, null=True, blank=True)
    posted_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    languages = models.ManyToManyField("Language", related_name="jobs")
    benefits = models.ManyToManyField("Benefit", related_name="jobs")
    ideal_resume = FileField(upload_to="ideal_resumes/", null=True, blank=True)
    cancel_reason = models.ForeignKey(
        "CancelReason", on_delete=models.SET_NULL, null=True, blank=True
    )  # when the job is cancelled, we ask clients reason to cancel it

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_attachments(self):
        return self.jobattachment_set.all()

    def get_languages(self):
        """Returns all languages associated with this job."""
        return self.languages.all()

    def get_benefits(self):
        """Returns all benefits associated with this job."""
        return self.benefits.all()

    def get_interview_steps(self):
        """Returns all interview steps associated with this job."""
        return self.interviewstep_set.all().order_by("uuid")

    def get_pending_applications(self):
        """Returns all pending applications for this job."""
        return RecruiterApplication.objects.filter(job=self, status=RecruiterApplication.ApplicationStatus.PENDING)

    def get_recruiters(self):
        """Returns all pending applications for this job."""
        return RecruiterApplication.objects.filter(job=self, status=RecruiterApplication.ApplicationStatus.APPROVED)


class JobAttachment(CoreModel):
    file = models.FileField(upload_to="job_attachments/", validators=[validate_file_extension])
    uploaded_by = models.ForeignKey("users.User", on_delete=models.CASCADE)  # Assuming User model exists
    job = models.ForeignKey("Job", on_delete=models.CASCADE, null=True, blank=True)  # Assuming Job model exists

    def __str__(self):
        return self.file.name

    @property
    def file_name(self):
        """Returns the name of the file."""
        return self.file.name.split("/")[-1]  # Extract file name from path

    @property
    def file_size(self):
        """Returns the file size in bytes."""
        return self.file.size if self.file else 0

    @property
    def file_type(self):
        """Returns the MIME type of the file, e.g., 'application/pdf'."""
        return self.file.file.content_type if self.file else None


class InterviewStep(CoreModel):
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    step_title = models.CharField(max_length=255)
    step_description = models.TextField(null=True, blank=True)
    priority = models.SmallIntegerField()

    class Meta:
        ordering = ["job", "step_title"]

    def __str__(self):
        return f"{self.step_title} for {self.job.title}"


class RecruiterApplication(CoreModel):
    class ApplicationStatus(models.IntegerChoices):
        PENDING = 0, "Pending"
        APPROVED = 1, "Approved"
        REJECTED = 2, "Rejected"

    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    recruiter = models.ForeignKey("recruiters.Recruiter", on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    approved_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Application for {self.job.title} by {self.recruiter.first_name} {self.recruiter.last_name}"


class JobNotes(CoreModel):
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    notes = models.TextField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Notes for Job {self.job}"
