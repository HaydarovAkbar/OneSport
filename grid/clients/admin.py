from django.contrib import admin

from .models import Address, Client, ClientUserProfile, Industry


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_name", "priority")
    search_fields = ("name",)
    ordering = ("name",)
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("company_name", "status", "industry", "country", "billing_email")
    list_filter = ("status", "industry", "country")
    search_fields = ("company_name", "billing_email", "billing_full_name", "phone")
    ordering = ("company_name",)
    readonly_fields = ("stripe_id",)  # Stripe ID should usually be read-only in the admin

    fieldsets = (
        (
            "Company Info",
            {"fields": ("company_name", "about", "phone", "linkedin", "company_size", "industry", "country", "logo")},
        ),
        ("Billing Information", {"fields": ("billing_full_name", "billing_email", "billing_phone")}),
        ("Status and Stripe Info", {"fields": ("status", "stripe_id")}),
        # ("Addresses", {"fields": ("addresses",)}),  # This will display as a multi-select field for M2M relationships
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("address1", "city", "zip_code", "state", "country", "client")
    search_fields = ("address1", "city", "zip_code", "client__name")  # assuming `client` has a `name` field
    list_filter = ("city", "state", "country")

    # Organize fields within the form view in the admin panel
    fieldsets = (
        (None, {"fields": ("client", "address1", "address2", "city", "zip_code")}),
        ("Location Details", {"fields": ("latitude", "longitude", "state", "country")}),
    )

    readonly_fields = (
        "latitude",
        "longitude",
    )  # Make fields read-only if they are auto-populated or shouldn't be edited

    # Customize the way addresses are saved (if necessary)
    def save_model(self, request, obj, form, change):
        # Customize save behavior if needed
        super().save_model(request, obj, form, change)


@admin.register(ClientUserProfile)
class ClientUserProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "user", "user_type", "client", "job_title")
    list_filter = ("user_type", "client")
    search_fields = ("first_name", "last_name", "user__username", "client__company_name", "job_title")
    ordering = ("last_name", "first_name")
    readonly_fields = ("get_profile_image",)  # Display profile image if available

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("first_name", "last_name", "linkedin", "job_title", "phone", "profile_photo")},
        ),
        ("User Info", {"fields": ("user", "user_type", "client")}),
        ("Profile Image", {"fields": ("get_profile_image",)}),  # This displays the image URL if available
    )

    @admin.display(description="Profile Image URL")
    def get_profile_image(self, obj):
        return obj.get_profile_image() or "No profile image available"
