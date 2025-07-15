from django.db import models
from django.utils.translation import gettext_lazy as _


class Roles(models.TextChoices):
    CLIENT = "CLIENT", _("Client")
    RECRUITER = "RECRUITER", _("Recruiter")
    ADMIN = "ADMIN", _("Admin")


class InviteStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    # EXPIRED = "EXPIRED", "Expired"
    DECLINED = "DECLINED", "Declined"


class InviteType(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    RECRUITER = "RECRUITER", "Recruiter"
