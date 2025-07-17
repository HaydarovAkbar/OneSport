from rest_framework import serializers

from ..clients.models import Address, Client
from ..users.models import User
from .models import Benefit, InterviewStep, Job, JobAttachment


class JobAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAttachment
        fields = ["uuid", "file", "uploaded_by"]
        read_only_fields = ["uuid", "uploaded_by"]

    def validate_attachments(self, value):
        for file in value:
            if not file.name.endswith(".pdf"):
                raise serializers.ValidationError("All attachments must be in .pdf format.")
        return value


class JobAttachmentDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAttachment
        fields = ["uuid"]
        read_only_fields = ["uuid"]


class CreateJobSerializer(serializers.ModelSerializer):
    salary_min = serializers.IntegerField(required=True, min_value=1)
    salary_max = serializers.IntegerField(required=False, min_value=1)
    attachments = serializers.ListField(child=serializers.UUIDField(), required=False, write_only=True)
    benefits = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Benefit.objects.all()), required=False, write_only=True
    )
    interview_steps = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, write_only=True
    )
    location = serializers.PrimaryKeyRelatedField(required=False, queryset=Address.objects.all())
    ideal_resume = serializers.FileField(required=False, allow_null=True, write_only=True, read_only=False)

    class Meta:
        model = Job
        fields = [
            "title",
            "no_of_roles",
            "description",
            "about_company",
            "must_haves",
            "nice_to_haves",
            "position_type",
            "job_type",
            "location",
            "benefits",
            "book_of_business",
            "min_book_of_business",
            "salary_min",
            "salary_max",
            "expected_commission",
            "signup_bonus",
            "stocks_value",
            "ideal_resume",
            "interview_steps",
            "attachments",
            "top_job",
        ]

    def validate(self, data):
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        if salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError("`salary_max` must be greater than or equal to `salary_min`.")
        return data

    def create(self, validated_data):
        attachment_uuids = validated_data.pop("attachments", [])
        benefits_data = validated_data.pop("benefits", [])
        interview_steps_data = validated_data.pop("interview_steps", [])
        location = validated_data.pop("location", None)
        ideal_resume = validated_data.pop("ideal_resume", None)
        validated_data["location"] = location if location else None

        job = Job.objects.create(**validated_data)

        job.benefits.add(*benefits_data)
        if ideal_resume:
            job.ideal_resume = ideal_resume
            job.save()

        JobAttachment.objects.filter(uuid__in=attachment_uuids).update(job=job)
        priority = 0
        for step_data in interview_steps_data:
            data = {"step_title": step_data}
            priority = priority + 1
            data["job"] = job
            data["priority"] = priority
            InterviewStep.objects.create(**data)

        return job


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "uuid",
            "title",
            "status",
            "no_of_roles",
            "description",
            "about_company",
            "must_haves",
            "nice_to_haves",
            "job_type",
            "position_type",
            "salary_min",
            "salary_max",
            "expected_commission",
            "signup_bonus",
            "stocks_value",
            "book_of_business",
            "top_job",
            "client",
            "location",
            "commission_percentage",
            "visa_sponsorship",
            "position_type",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, required=False)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    location = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), allow_null=True, required=False)
    posted_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    min_book_of_business = serializers.IntegerField(required=False, min_value=0)
    salary_min = serializers.IntegerField(required=False, min_value=1)
    benefits = serializers.PrimaryKeyRelatedField(queryset=Benefit.objects.all(), many=True, required=False)
    attachments = serializers.SerializerMethodField()
    interview_steps = serializers.SerializerMethodField()
    notes = serializers.CharField(required=False, allow_blank=True)
    about_company = serializers.CharField(required=False, allow_blank=True)
    nice_to_haves = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Job
        fields = [
            "title",
            "no_of_roles",
            "description",
            "about_company",
            "must_haves",
            "nice_to_haves",
            "position_type",
            "job_type",
            "location",
            "benefits",
            "book_of_business",
            "min_book_of_business",
            "salary_min",
            "salary_max",
            "expected_commission",
            "signup_bonus",
            "stocks_value",
            "ideal_resume",
            "interview_steps",
            "attachments",
            "top_job",
            "notes",
            "client",
            "posted_by",
        ]

    def get_interview_steps(self, obj):
        return [step.step_title for step in obj.interviewstep_set.all()]

    def get_attachments(self, obj):
        return [attachment.uuid for attachment in obj.jobattachment_set.all()]


class JobUpdateSerializer(serializers.ModelSerializer):
    benefits = serializers.PrimaryKeyRelatedField(queryset=Benefit.objects.all(), many=True, required=False)
    interview_steps = serializers.ListField(child=serializers.CharField(), required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    about_company = serializers.CharField(required=False, allow_blank=True)
    nice_to_haves = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Job
        fields = ["benefits", "interview_steps", "notes", "about_company", "nice_to_haves"]
