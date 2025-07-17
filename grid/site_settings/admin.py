from django.contrib import admin

from .models import (
    CommissionLevel,
    CompanySize,
    Country,
    Currency,
    PayoutInstalment,
    RecruiterShare,
    State,
)


@admin.register(CompanySize)
class CompanySizeAdmin(admin.ModelAdmin):
    list_display = ("name", "priority")
    search_fields = ("name",)
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "three_letter_code",
        "symbol",
        "job_posting_fee",
        "extra_role_fee",
        "top_job_fee",
        "salary_min",
        "commission_min",
        "financial_min",
    )
    search_fields = ("name", "three_letter_code", "symbol")
    list_filter = ("three_letter_code",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "two_letter_code", "three_letter_code", "icon_name", "currency", "priority")
    search_fields = ("name", "two_letter_code", "three_letter_code")
    list_filter = ("currency",)
    list_editable = ("priority",)
    ordering = ("priority",)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "two_letter_code",
        "country",
    )
    search_fields = ("name", "two_letter_code")
    list_filter = ("country",)


from django.contrib import admin

from .models import CommissionLevel, PayoutInstalment, RecruiterShare


@admin.register(RecruiterShare)
class RecruiterShareAdmin(admin.ModelAdmin):
    list_display = ("hires", "percentage", "default")
    list_filter = ("default",)
    search_fields = ("hires", "percentage")
    list_editable = ("percentage", "default")


@admin.register(CommissionLevel)
class CommissionLevelAdmin(admin.ModelAdmin):
    list_display = ("title", "min_commission", "max_commission")
    search_fields = ("title", "message")
    list_filter = ("min_commission", "max_commission")


@admin.register(PayoutInstalment)
class PayoutInstalmentAdmin(admin.ModelAdmin):
    list_display = ("name", "percentage", "interval_in_days")
    search_fields = ("name",)
    list_filter = ("interval_in_days",)
