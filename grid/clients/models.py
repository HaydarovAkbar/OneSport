from django.core.exceptions import ValidationError
from django.db import models

from grid.core.models import CoreModel
from grid.site_settings.models import Country


class Industry(CoreModel):
    name = models.CharField(max_length=255)
    icon_name = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(default=10)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name


def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10 MB in bytes
    if image.size > max_size:
        raise ValidationError("The image size should not exceed 10 MB.")


def get_client_logo_path(instance, filename):
    """Generate path for client company logos
    Format: clients/logos/client_uuid/filename
    """
    ext = filename.split(".")[-1]
    return f"clients/logos/{instance.uuid}/logo.{ext}"


def get_client_profile_photo_path(instance, filename):
    """Generate path for client user profile photos
    Format: clients/profile_photos/client_uuid/user_uuid/filename
    """
    ext = filename.split(".")[-1]
    return f"clients/profile_photos/{instance.client.uuid}/{instance.user.uuid}/profile.{ext}"


class Client(CoreModel):
    class Status(models.IntegerChoices):
        ACTIVE = 1, "Active"
        PENDING_APPROVAL = 2, "Pending Approval"
        PENDING_SIGNUP = 3, "Pending Signup"
        WAIT_LIST = 4, "Wait list"
        REJECTED = 5, "Rejected"

    company_name = models.CharField(max_length=255)
    about = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    company_size = models.CharField(max_length=255, null=True, blank=True)
    linkedin_company_size = models.IntegerField(null=True, blank=True)
    billing_full_name = models.CharField(max_length=255, null=True, blank=True)
    billing_email = models.EmailField(null=True, blank=True)
    billing_phone = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to=get_client_logo_path, validators=[validate_image_size], null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.RESTRICT, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, null=True, blank=True)
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.PENDING_SIGNUP)

    class Meta:
        ordering = ["company_name"]
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.company_name


class ClientUserProfile(CoreModel):
    class UserType(models.IntegerChoices):
        SUPERUSER = 0, "Superadmin"
        ADMIN = 1, "Admin"
        MEMBER = 2, "Member"

    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    linkedin = models.CharField(max_length=500, null=True, blank=True)
    job_title = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    user_type = models.SmallIntegerField(choices=UserType.choices, default=UserType.MEMBER)
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to=get_client_profile_photo_path, validators=[validate_image_size], max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Address(CoreModel):
    name = models.CharField(max_length=255, default="HQ")
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.ForeignKey(
        "site_settings.State", on_delete=models.RESTRICT
    )  # Assuming a foreign key to a State model
    country = models.ForeignKey(
        "site_settings.Country", on_delete=models.RESTRICT
    )  # Assuming a foreign key to a Country model
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # For latitude
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # For longitude
    client = models.ForeignKey("Client", on_delete=models.CASCADE, related_name="addresses", null=True, blank=True)
    by_user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["city"]

    @property
    def full_address(self):
        address_lines = [self.address1]
        if self.address2:
            address_lines.append(self.address2)
        # Add city, state, and zip code on the next line
        address_lines.append(f"{self.city}, {self.state.name} {self.zip_code}")
        return "\n".join(address_lines)

    def __str__(self):
        return self.full_address

    def __str__(self):
        return f"{self.address1}, {self.city}"
