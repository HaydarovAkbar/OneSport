import secrets
import string

from django.db import models
from django.utils.timezone import now

from grid.candidates.models import Candidate
from grid.clients.models import Client
from grid.core.models import CoreModel
from grid.jobs.models import Job
from grid.recruiters.models import Recruiter
from grid.site_settings.models import Currency


class Hire(CoreModel):
    class PaymentStatus(models.IntegerChoices):
        DUE = 0, "Due"
        PAID = 1, "Paid"
        REFUNDED = 2, "Refunded"
        CANCELLED = 3, "Cancelled"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="hire_job")
    base_salary = models.FloatField()
    payment_status = models.SmallIntegerField(choices=PaymentStatus.choices, default=PaymentStatus.DUE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name="hire_recruiter")
    join_date = models.DateTimeField(null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="hire_candidate")
    payout = models.FloatField()
    commission = models.FloatField()
    commission_percentage = models.SmallIntegerField()

    class Meta:
        ordering = ["-join_date"]

    def __str__(self):
        return f"Hire for {self.candidate} in Job {self.job}"


class RecruiterPayment(CoreModel):
    class RecruiterPaymentStatus(models.IntegerChoices):
        PENDING = 0, "Pending"
        PAID = 1, "Paid"
        DUE = 2, "Due"
        CANCELLED = 3, "Cancelled"

    amount = models.FloatField()
    due_on = models.DateTimeField()
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, related_name="recruiter_payment")
    hire = models.ForeignKey(Hire, on_delete=models.CASCADE, related_name="hire_payment")
    status = models.SmallIntegerField(choices=RecruiterPaymentStatus.choices, default=RecruiterPaymentStatus.PENDING)
    percentage_of_full = models.SmallIntegerField()

    class Meta:
        ordering = ["-due_on"]

    def __str__(self):
        return f"Payment of {self.amount} for Hire {self.hire}"


def generate_unique_code():
    """Generate cryptographically secure unique code for invoices."""
    length = 8
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))  # Use secrets instead of random


class Invoice(CoreModel):
    class InvoiceStatus(models.IntegerChoices):
        DUE = 1, "Due"
        PAID = 2, "Paid"
        VOID = 3, "Void"
        REFUNDED = 4, "Refunded"

    invoice_code = models.CharField(max_length=8, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="invoices")
    hire = models.OneToOneField(Hire, on_delete=models.CASCADE, related_name="invoice")
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    due_date = models.DateTimeField()
    product_name = models.CharField(max_length=255, default="Recruitment Services")
    description = models.TextField(default="Commission for successful hiring of an employee")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_name = models.CharField(max_length=100, default="GST/HST/VAT")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.SmallIntegerField(choices=InvoiceStatus.choices, default=InvoiceStatus.DUE)

    @property
    def subtotal(self):
        """Subtotal before tax."""
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        """Tax amount based on subtotal and tax percentage."""
        return (self.tax_percentage / 100) * self.subtotal

    @property
    def total(self):
        """Total amount including tax."""
        return self.subtotal + self.tax_amount

    @property
    def overdue(self):
        """Checks if the invoice is overdue."""
        return self.status == self.InvoiceStatus.DUE and self.due_date < now()

    def save(self, *args, **kwargs):
        if not self.invoice_code:
            self.invoice_code = self.generate_unique_code()
            # Ensure uniqueness by regenerating if necessary
            while Invoice.objects.filter(invoice_code=self.invoice_code).exists():
                self.invoice_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        return generate_unique_code()

    def __str__(self):
        return f"Invoice {self.invoice_code} for {self.client.company_name}"
