from django.contrib import admin

from .models import Candidate, Skill, Stage, StageLog


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_name", "description", "priority")
    search_fields = ("name", "description")
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "recruiter", "stage", "job", "email")
    list_filter = ("recruiter", "stage", "job")
    search_fields = ("first_name", "last_name", "email", "job__title", "recruiter__first_name", "recruiter__last_name")
    ordering = ("last_name", "first_name")
    fieldsets = (
        (
            "Personal Information",
            {"fields": ("first_name", "last_name", "recruiter", "email", "phone", "linkedin", "profile_photo")},
        ),
        ("Job and Skills", {"fields": ("stage", "job", "skills")}),
        ("Resumes", {"fields": ("original_resume", "formatted_resume", "edited_resume")}),
    )


@admin.register(StageLog)
class StageLogAdmin(admin.ModelAdmin):
    list_display = ("candidate", "from_stage", "to_stage", "user")
    search_fields = (
        "candidate__first_name",
        "candidate__last_name",
        "from_stage__name",
        "to_stage__name",
        "user__username",
    )
    ordering = ("candidate",)
