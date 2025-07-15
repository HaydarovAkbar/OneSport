from django.contrib import admin

from .models import (
    Benefit,
    CancelReason,
    InterviewStep,
    Job,
    JobAttachment,
    Language,
    RecruiterApplication,
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "priority")
    search_fields = ("name",)
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_name", "description", "priority")
    search_fields = ("name", "description")
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(CancelReason)
class CancelReasonAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "priority")
    search_fields = ("name", "description")
    ordering = ("priority",)
    list_editable = ("priority",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "client", "job_type", "position_type", "salary_min", "salary_max")
    list_filter = ("status", "job_type", "position_type", "client", "category")
    search_fields = ("title", "client__company_name", "description")
    ordering = ("title",)
    fieldsets = (
        (
            "Job Information",
            {"fields": ("title", "description", "about_company", "must_haves", "nice_to_haves", "status")},
        ),
        ("Job Type and Position", {"fields": ("job_type", "position_type", "top_job", "book_of_business")}),
        (
            "Compensation",
            {
                "fields": (
                    "salary_min",
                    "salary_max",
                    "expected_commission",
                    "signup_bonus",
                    "stocks_value",
                    "commission_percentage",
                )
            },
        ),
        (
            "Other Details",
            {
                "fields": (
                    "visa_sponsorship",
                    "client",
                    "location",
                    "category",
                    "posted_by",
                    "languages",
                    "benefits",
                    "ideal_resume",
                    "cancel_reason",
                )
            },
        ),
    )


@admin.register(JobAttachment)
class JobAttachmentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "file_size", "file_type", "uploaded_by", "job")
    search_fields = ("file_name", "job__title")
    list_filter = ("job", "uploaded_by")
    ordering = ("job",)


@admin.register(InterviewStep)
class InterviewStepAdmin(admin.ModelAdmin):
    list_display = ("step_title", "job", "step_description")
    search_fields = ("step_title", "job__title")
    ordering = ("job", "step_title")


@admin.register(RecruiterApplication)
class RecruiterApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "recruiter", "status", "approved_date")
    list_filter = ("status", "job", "recruiter")
    search_fields = ("job__title", "recruiter__first_name", "recruiter__last_name")
    ordering = ("-approved_date",)
