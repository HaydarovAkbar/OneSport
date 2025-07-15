from django.db import models

from grid.core.models import CoreModel
from grid.jobs.models import Job


class Skill(CoreModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Stage(CoreModel):
    name = models.CharField(max_length=255)
    icon_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Candidate(CoreModel):
    class ShowResume(models.IntegerChoices):
        ORIGINAL = 0, "Original"
        FORMATTED = 1, "Formatted"
        EDITED = 2, "Edited"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    recruiter = models.ForeignKey("recruiters.Recruiter", on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/")
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name="candidates")
    status = models.SmallIntegerField(choices=ShowResume.choices, default=ShowResume.FORMATTED)
    is_interviewed = models.BooleanField(default=False)

    # Resume fields
    original_resume = models.FileField(upload_to="resumes/originals/", null=True, blank=True)
    formatted_resume = models.FileField(upload_to="resumes/formatted/", null=True, blank=True)
    edited_resume = models.FileField(upload_to="resumes/edited/", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Optional properties for convenience
    @property
    def original_resume_size(self):
        return self.original_resume.size if self.original_resume else None

    @property
    def formatted_resume_size(self):
        return self.formatted_resume.size if self.formatted_resume else None

    @property
    def edited_resume_size(self):
        return self.edited_resume.size if self.edited_resume else None


class StageLog(CoreModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    from_stage = models.ForeignKey(
        Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name="from_stage_logs"
    )
    to_stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name="to_stage_logs")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Stage change for {self.candidate} by {self.user}"
