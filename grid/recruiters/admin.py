from django.contrib import admin

from .models import Agency, BankAccount, JobCategory, Recruiter, TaxInformation


@admin.register(TaxInformation)
class TaxInformationAdmin(admin.ModelAdmin):
    list_display = ("agency", "ein", "tin", "business_number", "sin", "vat", "utr", "abn")
    search_fields = ("ein", "tin", "business_number", "sin", "vat", "utr", "abn")


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_name", "priority")
    search_fields = ("name",)
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("agency", "account_name", "account_number", "bank_name")
    search_fields = ("account_name", "account_number", "bank_name")
    ordering = ("account_name",)
    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "account_name",
                    "account_number",
                    "routing_number",
                    "institution_number",
                    "transit_number",
                    "sort_code",
                    "bsb_code",
                    "bank_address",
                    "account_address",
                )
            },
        ),
        ("Bank Details", {"fields": ("bank_name", "agency")}),
    )


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("agency_name", "make_payable_to", "is_individual")
    list_filter = ("is_individual",)
    search_fields = ("agency_name", "make_payable_to", "linkedin")
    ordering = ("agency_name",)

    # Optional inline display for BankAccount and TaxInformation within Agency
    class BankAccountInline(admin.StackedInline):
        model = BankAccount
        fields = ("account_name", "account_number", "bank_name")
        extra = 0  # Prevent extra blank rows

    class TaxInformationInline(admin.StackedInline):
        model = TaxInformation
        fields = ("ein", "tin", "business_number", "sin", "vat", "utr", "abn")
        extra = 0  # Prevent extra blank rows

    inlines = [BankAccountInline, TaxInformationInline]


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = (
        "is_active",
        "first_name",
        "last_name",
        "user",
        "primary_industry",
        "sec_industry",
        "status",
        "superuser",
        "approval_date",
    )
    list_filter = ("status", "superuser", "primary_industry", "sec_industry")
    search_fields = ("first_name", "last_name", "user__username", "agency__agency_name", "linkedin")
    ordering = ("last_name", "first_name")
    readonly_fields = ("stripe_id",)  # Stripe ID is read-only
    fieldsets = (
        (
            "Personal Information",
            {"fields": ("user", "first_name", "last_name", "phone", "profile_photo", "linkedin", "address")},
        ),
        (
            "Professional Information",
            {
                "fields": (
                    "primary_industry",
                    "sec_industry",
                    "agency",
                    "status",
                    "superuser",
                    "commission_share",
                    "approval_date",
                )
            },
        ),
        ("Payment Details", {"fields": ("stripe_id",)}),
        ("Additional Information", {"fields": ("introduction", "story")}),
    )
