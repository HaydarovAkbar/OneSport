from django.core.exceptions import ValidationError
from django.db import models

from grid.core.models import CoreModel


# Create your models here.
class AdminUserProfile(CoreModel):
    class UserType(models.IntegerChoices):
        SUPERADMIN = 1
        ADMIN = 2
        EDITOR = 3
        VIEWER = 4
        ACCOUNTANT = 5

    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    user_type = models.IntegerField(choices=UserType.choices, default=UserType.VIEWER)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"
