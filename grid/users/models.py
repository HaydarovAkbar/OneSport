import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from grid.core.models import CoreModel
from grid.users.choices import InviteStatus, InviteType, Roles
from grid.users.managers import CustomUserManager


class User(AbstractUser, CoreModel):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT, verbose_name=_("role"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_client(self):
        return self.role == Roles.CLIENT

    @property
    def is_recruiter(self):
        return self.role == Roles.RECRUITER

    @property
    def is_admin(self):
        return self.role == Roles.ADMIN

    @cached_property
    def team_invite(self):
        """
        Returns the accepted team invite with related inviter data
        """
        return (
            TeamInvite.objects.select_related("inviter__clientuserprofile__client", "inviter__recruiter__agency")
            .filter(email=self.email, status=InviteStatus.ACCEPTED)
            .first()
        )

    @property
    def is_team_member(self):
        """
        Returns True if user was invited as a team member (has accepted invite)
        """
        # TODO: Update this with a better logic when teams functionality is included
        return bool(self.team_invite)

    @property
    def owner_profile(self):
        """
        Returns organization owner's profile (client/recruiter) if user is team member
        """
        if not self.team_invite:
            return None

        if self.team_invite.invite_type == InviteType.CLIENT:
            return self.team_invite.inviter.clientuserprofile.client
        return self.team_invite.inviter.recruiter


class TeamInvite(CoreModel):
    email = models.EmailField()
    inviter = models.ForeignKey("users.User", on_delete=models.DO_NOTHING, related_name="sent_invites")
    invite_type = models.CharField(max_length=10, choices=InviteType.choices, default=InviteType.CLIENT)
    status = models.CharField(max_length=10, choices=InviteStatus.choices, default=InviteStatus.PENDING)
    token = models.CharField(max_length=255, unique=True)
    # expires_at = models.DateTimeField()
    data = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        # if not self.expires_at:
        #     self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
