from django.contrib import admin

from .models import AdminUserProfile


@admin.register(AdminUserProfile)
class AdminUserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "user_type_display")
    search_fields = ("user__email", "first_name", "last_name")
    list_filter = ("user_type",)
    fieldsets = (
        (None, {"fields": ("user", "user_type")}),
        ("Personal Information", {"fields": ("first_name", "last_name")}),
    )

    @admin.display(description="User Type")
    def user_type_display(self, obj):
        return obj.get_user_type_display()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
