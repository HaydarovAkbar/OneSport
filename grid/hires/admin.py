from django.contrib import admin

from .models import Hire, RecruiterPayment


@admin.register(Hire)
class HireAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "recruiter", "base_salary", "payment_status", "join_date")
    list_filter = ("payment_status", "recruiter", "job")
    search_fields = (
        "candidate__first_name",
        "candidate__last_name",
        "job__title",
        "recruiter__first_name",
        "recruiter__last_name",
    )
    ordering = ("-join_date",)


@admin.register(RecruiterPayment)
class RecruiterPaymentAdmin(admin.ModelAdmin):
    list_display = ("amount", "status", "due_on", "hire", "currency")
    list_filter = ("status", "currency")
    search_fields = ("hire__candidate__first_name", "hire__candidate__last_name", "amount")
    ordering = ("-due_on",)
