from django.core.exceptions import ValidationError
from django.db import models

from grid.clients.models import Address
from grid.core.models import CoreModel


class Agency(CoreModel):
    agency_name = models.CharField(max_length=255, null=True, blank=True)
    make_payable_to = models.CharField(max_length=255)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    is_individual = models.BooleanField(default=True)

    class Meta:
        ordering = ["agency_name"]
        verbose_name_plural = "Agencies"

    @classmethod
    def create_from_agency_info(cls, agency_info_data, user):
        """
        Creates a new agency instance with the provided information
        """
        website = agency_info_data.pop("website", None)  # Get website and use it as linkedin

        agency = cls.objects.create(
            agency_name=agency_info_data.get("agency_name"),
            make_payable_to=agency_info_data["make_payable_to"],
            is_individual=agency_info_data["is_individual"],
            linkedin=website,  # Store website in linkedin field
        )

        return agency

    def __str__(self):
        return self.agency_name if self.agency_name else self.make_payable_to


class TaxInformation(CoreModel):
    agency = models.OneToOneField(
        "Agency", on_delete=models.SET_NULL, null=True, blank=True, related_name="tax_information"
    )
    ein = models.CharField(max_length=50, null=True, blank=True)  # Employer Identification Number
    tin = models.CharField(max_length=50, null=True, blank=True)  # Tax Identification Number
    business_number = models.CharField(max_length=50, null=True, blank=True)  # Business Number
    sin = models.CharField(max_length=50, null=True, blank=True)  # Social Insurance Number
    vat = models.CharField(max_length=50, null=True, blank=True)  # Value Added Tax number
    utr = models.CharField(max_length=50, null=True, blank=True)  # Unique Taxpayer Reference
    abn = models.CharField(max_length=50, null=True, blank=True)  # Australian Business Number

    def __str__(self):
        return f"Tax Information {self.id}"


class BankAccount(CoreModel):
    agency = models.OneToOneField(
        "Agency", on_delete=models.CASCADE, null=True, blank=True, related_name="bank_account"
    )
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50, null=True, blank=True)
    institution_number = models.CharField(max_length=50, null=True, blank=True)
    transit_number = models.CharField(max_length=50, null=True, blank=True)
    sort_code = models.CharField(max_length=50, null=True, blank=True)
    bsb_code = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_address = models.CharField(max_length=255, null=True, blank=True)
    account_address = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["account_name"]

    def __str__(self):
        return f"{self.account_name}"


class JobCategory(CoreModel):
    name = models.CharField(max_length=255)
    icon_name = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Job Categories"

    def __str__(self):
        return self.name


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10 MB in bytes
    if image.size > max_size:
        raise ValidationError("The image size should not exceed 10 MB.")


def get_recruiter_photo_path(instance, filename):
    """
    Generate path for recruiter profile photos
    Format: user_uuid/recruiters/profile_photos/recruiter_uuid/filename
    """
    ext = filename.split(".")[-1]
    new_filename = f"profile_photo.{ext}"
    return f"recruiters/profile_photos/{instance.uuid}/{new_filename}"


class Recruiter(CoreModel):
    class RecruiterStatus(models.IntegerChoices):
        ACTIVE = 0, "Active"
        PENDING_APPROVAL = 1, "Pending Approval"
        PENDING_SIGNUP = 2, "Pending Signup"
        WAIT_LIST = 3, "Wait list"
        REJECTED = 4, "Rejected"

    user = models.OneToOneField("users.User", on_delete=models.RESTRICT)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    story = models.TextField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    primary_industry = models.ForeignKey(
        "JobCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="primary_recruiters"
    )
    sec_industry = models.ForeignKey(
        "JobCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="secondary_recruiters"
    )
    address = models.ForeignKey("clients.Address", on_delete=models.SET_NULL, null=True, blank=True)
    commission_share = models.SmallIntegerField(null=True, blank=True)
    status = models.SmallIntegerField(choices=RecruiterStatus.choices, default=RecruiterStatus.PENDING_SIGNUP)
    agency = models.ForeignKey("Agency", on_delete=models.SET_NULL, null=True, blank=True, related_name="recruiters")
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to=get_recruiter_photo_path, validators=[validate_image_size], blank=True, null=True
    )
    linkedin = models.URLField(max_length=255)
    superuser = models.BooleanField(default=False)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
