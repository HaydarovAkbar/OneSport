from rest_framework import serializers

from grid.clients.models import Address, Client, ClientUserProfile, Industry
from grid.recruiters.serializers import AddressSerializer


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "uuid",
            "company_name",
            "about",
            "phone",
            "linkedin",
            "company_size",
            "linkedin_company_size",
            "billing_full_name",
            "billing_email",
            "billing_phone",
            "logo",
            "industry",
            "country",
            "stripe_id",
            "status",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "stripe_id": {"read_only": True},
            "status": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context.get("request").user

        # Hide sensitive fields for non-admin users
        if not user.is_admin:
            sensitive_fields = ["linkedin_company_size", "stripe_id", "status"]
            for field in sensitive_fields:
                data.pop(field, None)

        return data

    def validate(self, data):
        user = self.context.get("request").user

        if not user.is_admin:
            # Check if user has permission to edit
            try:
                profile = user.clientuserprofile
                restricted_fields = ["stripe_id", "status"]
                if profile.user_type not in [ClientUserProfile.UserType.SUPERUSER, ClientUserProfile.UserType.ADMIN]:
                    raise serializers.ValidationError("Only superadmin and admin users can modify client details")
                # Check initial data before serializer processing
                initial_data = getattr(self, "initial_data", {})
                for field in restricted_fields:
                    if field in initial_data:
                        raise serializers.ValidationError({field: f"You cannot modify {field}"})
                # Ensure user belongs to this client
                if self.instance and profile.client != self.instance:
                    raise serializers.ValidationError("You can only modify your own client's details")
            except ClientUserProfile.DoesNotExist:
                raise serializers.ValidationError("User profile not found")

        return data


class ClientUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUserProfile
        fields = [
            "uuid",
            "user",
            "first_name",
            "last_name",
            "linkedin",
            "job_title",
            "phone",
            "user_type",
            "client",
            "profile_photo",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "user": {"read_only": True},
            "client": {"read_only": True},
        }

    def validate(self, data):
        request = self.context.get("request")
        user = request.user if request else None

        if not user:
            raise serializers.ValidationError("User context is required")

        if not user.is_admin:
            # Ensure user can only modify their own profile
            if self.instance and self.instance.user != user:
                raise serializers.ValidationError("You can only modify your own profile")

            # Prevent modification of user_type by non-admin users
            if "user_type" in self.initial_data:
                raise serializers.ValidationError({"user_type": "You cannot modify user type"})

        return data


class ClientBasicInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=255, required=False)
    job_title = serializers.CharField(max_length=500, required=False)
    company_linkedin = serializers.URLField(max_length=255, required=False)

    def validate_company_linkedin(self, value):
        """Ensure the URL is a company LinkedIn URL"""
        if "/company/" not in value:
            raise serializers.ValidationError("Please provide a company LinkedIn URL")
        return value


class ClientCompanyInfoSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255)
    website = serializers.URLField(required=False)
    industry = serializers.UUIDField()
    linkedin_company_size = serializers.IntegerField(min_value=1, required=True)
    address = AddressSerializer()
    logo_url = serializers.URLField(required=False)
    profile_pic_url = serializers.URLField(required=False)

    def validate_industry(self, value):
        """
        Validate that the industry UUID exists
        Returns the Industry instance if valid
        """
        try:
            return Industry.objects.get(uuid=value)
        except Industry.DoesNotExist:
            raise serializers.ValidationError("Invalid industry selected")


class ClientSignupResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    client = serializers.UUIDField()
    client_profile = serializers.UUIDField()
    address = serializers.UUIDField(required=False)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["client", "by_user"]
        ref_name = "GeneralAddress"

    def create(self, validated_data):
        validated_data["client"] = self.context["request"].user.clientuserprofile.client
        validated_data["by_user"] = self.context["request"].user
        return super().create(validated_data)
