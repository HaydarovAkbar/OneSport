from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from grid.clients.models import ClientUserProfile
from grid.users.choices import InviteStatus, InviteType, Roles
from grid.users.models import TeamInvite, User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        try:
            EmailAddress.objects.get(user=user, verified=True)
        except EmailAddress.DoesNotExist:
            raise AuthenticationFailed("Email not verified")

        return data


class CustomUserRegisterSerializer(RegisterSerializer):
    username = None  # Remove username field
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=Roles.choices, default=Roles.CLIENT)

    def get_cleaned_data(self):
        return {
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "role": self.validated_data.get("role", ""),
        }


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "role",
            "created_at",
            "updated_at",
            "last_login",
        )
        read_only_fields = ("email", "created_at", "updated_at", "last_login")


class RouteResponseSerializer(serializers.Serializer):
    route = serializers.CharField()
    message = serializers.CharField()
    role = serializers.CharField()
    uuid = serializers.UUIDField(allow_null=True, required=False)
    is_member = serializers.BooleanField()


class TeamInviteSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(
        write_only=True, help_text="Type of user to invite (ADMIN/MEMBER for clients, MEMBER for recruiters)"
    )

    class Meta:
        model = TeamInvite
        fields = ["email", "user_type", "uuid", "created_at", "updated_at", "inviter", "invite_type"]
        read_only_fields = ["uuid", "created_at", "updated_at", "inviter", "invite_type"]
        extra_kwargs = {"email": {"help_text": "Email address of the person to invite"}}

    def validate_user_type(self, value):
        user = self.context["request"].user

        if user.is_client:
            valid_types = [ClientUserProfile.UserType.ADMIN.name, ClientUserProfile.UserType.MEMBER.name]
            if value not in valid_types:
                raise serializers.ValidationError(
                    f"Invalid user type for client team member. Must be one of: {', '.join(valid_types)}"
                )
        elif user.is_recruiter:
            if value != "MEMBER":
                raise serializers.ValidationError("Recruiter team members can only be regular members")
        return value

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if EmailAddress.objects.is_verified(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."),
            )
        return email

    def validate(self, data):
        user = self.context["request"].user

        # Determine invite type based on inviter's role
        if user.is_client:
            data["invite_type"] = InviteType.CLIENT

        elif user.is_recruiter:
            data["invite_type"] = InviteType.RECRUITER

        else:
            raise serializers.ValidationError("Invalid user role for sending invites")

        return data

    def create(self, validated_data):
        user_type = validated_data.pop("user_type")
        invite_type = validated_data["invite_type"]
        inviter = self.context["request"].user
        # Prepare role-specific data
        if invite_type == InviteType.CLIENT:
            data = {"user_type": user_type}
        else:  # RECRUITER
            data = {
                "user_type": "MEMBER",
            }
        # Create the invite with the prepared data
        return TeamInvite.objects.create(**validated_data, inviter=inviter, data=data)


class MemberRegisterSerializer(serializers.Serializer):
    token = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_token(self, value):
        if not TeamInvite.objects.filter(token=value, status=InviteStatus.PENDING).exists():
            raise serializers.ValidationError("Invalid or expired invitation token")
        return value

    def validate_password1(self, password1):
        return get_adapter().clean_password(password1)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def create(self, validated_data):
        token = validated_data.pop("token")
        password1 = validated_data.pop("password1")
        invite = TeamInvite.objects.get(token=token)

        with transaction.atomic():
            # Create user based on invite type
            user = User.objects.create(
                email=invite.email,
                role=Roles.CLIENT if invite.invite_type == InviteType.CLIENT else Roles.RECRUITER,
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            user.password = make_password(password1)
            user.save()

            # Create and verify email address using allauth
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)

            # Update invite status
            invite.status = InviteStatus.ACCEPTED
            invite.save()

            return user
