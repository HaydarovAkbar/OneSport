from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from grid.users.models import TeamInvite


User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "uuid",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_superuser",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    # "profile_image",
                    "role",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    ordering = ("email",)
    search_fields = (
        "uuid",
        "email",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "invite_type",
        "status",
        "created_at",
        "inviter_info",
        "invite_link",
    ]

    list_filter = ["status", "invite_type", "created_at"]

    search_fields = ["email", "inviter__email", "token"]

    readonly_fields = ["token", "created_at", "updated_at"]

    fieldsets = (
        (
            "Invite Information",
            {
                "fields": (
                    "email",
                    "invite_type",
                    "status",
                    "inviter",
                    "token",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(
        description="Inviter",
        ordering="inviter__email",
    )
    def inviter_info(self, obj):
        """Display inviter's email and role"""
        if obj.inviter.is_client:
            role = "Client"
            company = obj.inviter.clientuserprofile.client.company_name
        else:
            role = "Recruiter"
            company = obj.inviter.recruiter.agency.agency_name

        return format_html(
            '<span title="Company: {}">{}<br/><small>{}</small></span>', company, obj.inviter.email, role
        )

    @admin.display(description="Invite Link")
    def invite_link(self, obj):
        """Display the invite link with copy button"""
        invite_url = f"{settings.FRONTEND_URL}/invite/{obj.token}"
        return format_html(
            '<input type="text" value="{}" style="width: 200px;" readonly>'
            "<button onclick=\"navigator.clipboard.writeText('{}')\">Copy</button>",
            invite_url,
            invite_url,
        )

    def get_queryset(self, request):
        """Optimize queries by prefetching related data"""
        qs = super().get_queryset(request)
        return qs.select_related("inviter", "inviter__clientuserprofile__client", "inviter__recruiter__agency")
