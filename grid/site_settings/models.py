from django.core.exceptions import ValidationError
from django.db import models

from grid.core.models import CoreModel


class RecruiterShare(CoreModel):
    hires = models.SmallIntegerField()
    percentage = models.SmallIntegerField()
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"Recruiter Share: {self.percentage}% for {self.hires} hires"


class CompanySize(CoreModel):
    name = models.CharField(max_length=255)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class CommissionLevel(CoreModel):
    min_commission = models.SmallIntegerField()
    max_commission = models.SmallIntegerField()
    message = models.TextField()
    title = models.CharField(max_length=255)
    message2 = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.min_commission}% - {self.max_commission}%)"

    class Meta:
        ordering = ["min_commission"]


class PayoutInstalment(CoreModel):
    name = models.CharField(max_length=255)
    percentage = models.SmallIntegerField()
    interval_in_days = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}: {self.percentage}% every {self.interval_in_days} days"


class Timezone(CoreModel):
    name = models.CharField(max_length=1000)
    utc_offset = models.DecimalField(max_digits=4, decimal_places=2)  # Offset in hours
    utc_offset_dst = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # DST offset
    is_dst = models.BooleanField(default=False)  # DST active status
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    start_dst = models.DateTimeField(null=True, blank=True)  # DST start date
    end_dst = models.DateTimeField(null=True, blank=True)  # DST end date

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10 MB in bytes
    if image.size > max_size:
        raise ValidationError("The image size should not exceed 10 MB.")


class Currency(CoreModel):
    name = models.CharField(max_length=255)
    three_letter_code = models.CharField(max_length=3, unique=True)  # ISO 3-letter currency code
    symbol = models.CharField(max_length=10, null=True, blank=True)  # Currency symbol
    job_posting_fee = models.FloatField()
    extra_role_fee = models.FloatField()
    top_job_fee = models.FloatField()
    salary_min = models.FloatField()
    commission_min = models.FloatField()
    financial_min = models.FloatField(null=True, blank=True)
    future_fee1 = models.FloatField(null=True, blank=True)
    future_fee2 = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.name} ({self.three_letter_code})"


class Country(CoreModel):
    name = models.CharField(max_length=255)
    two_letter_code = models.CharField(max_length=2)  # ISO 2-letter country code
    three_letter_code = models.CharField(max_length=3)  # ISO 3-letter country code
    icon_name = models.CharField(max_length=255, null=True, blank=True)  # icon name from CSS library used
    currency = models.ForeignKey(
        Currency, on_delete=models.RESTRICT, related_name="countries"
    )  # Foreign key to Currency
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["priority"]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class State(CoreModel):
    name = models.CharField(max_length=255)
    two_letter_code = models.CharField(max_length=4)  # 4-letter abbreviation
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, related_name="states")
    tax_name = models.CharField(max_length=15, default="Tax", null=True, blank=True)
    tax_percentage = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
