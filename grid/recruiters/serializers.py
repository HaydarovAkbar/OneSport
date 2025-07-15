from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from grid.clients.models import Address
from grid.core.validators import validate_linkedin_profile_url, validate_phone_number
from grid.recruiters.models import Agency, BankAccount, JobCategory, Recruiter
from grid.recruiters.utils import process_person_linkedin_data
from grid.users.choices import InviteStatus
from grid.users.models import TeamInvite


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = "__all__"
        extra_kwargs = {
            "status": {"read_only": True},
            "primary_industry": {"read_only": True},
            "sec_industry": {"read_only": True},
            "commission_share": {"read_only": True},
            "agency": {"read_only": True},
            "superuser": {"read_only": True},
            "uuid": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context.get("request").user

        # Hide stripe_id for non-admin users
        if not user.is_admin:
            data.pop("stripe_id", None)

        return data

    def validate(self, data):
        request = self.context.get("request")
        user = request.user if request else None

        if not user:
            raise serializers.ValidationError("User context is required")

        # Check if user is trying to modify restricted fields
        if user.is_recruiter and not user.is_admin:
            restricted_fields = [
                "status",
                "primary_industry",
                "sec_industry",
                "commission_share",
                "agency",
                "superuser",
                "uuid",
                "created_at",
                "updated_at",
            ]

            # Check initial data before serializer processing
            initial_data = getattr(self, "initial_data", {})
            for field in restricted_fields:
                if field in initial_data:
                    raise serializers.ValidationError({field: f"You cannot modify {field}"})

            # Address restrictions
            if "address" in data:
                address_data = self.initial_data.get("address", {})
                if isinstance(address_data, dict):
                    if "country" in address_data or "state" in address_data:
                        raise serializers.ValidationError({"address": "You cannot modify country or state in address"})

        return data


class RestrictedRecruiterSerializer(RecruiterSerializer):
    """Serializer for non-superuser recruiters"""

    class Meta(RecruiterSerializer.Meta):
        read_only_fields = [
            "status",
            "primary_industry",
            "sec_industry",
            "commission_share",
            "agency",
            "superuser",
            "uuid",
            "created_at",
            "updated_at",
        ]


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = "__all__"
        extra_kwargs = {
            "is_individual": {"read_only": True},
            "uuid": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context.get("request").user

        # For non-superuser recruiters, hide sensitive fields
        if user.is_recruiter and not user.recruiter.superuser:
            sensitive_fields = ["is_individual", "make_payable_to", "linkedin"]
            for field in sensitive_fields:
                data.pop(field, None)

        return data

    def validate(self, data):
        request = self.context.get("request")
        user = request.user if request else None

        if not user:
            raise serializers.ValidationError("User context is required")

        # Only admin and superuser recruiters can edit
        if user.is_recruiter:
            if not user.recruiter.superuser:
                raise serializers.ValidationError("Only superuser recruiters can modify agency details")

            # Check if user belongs to this agency
            if self.instance and user.recruiter.agency != self.instance:
                raise serializers.ValidationError("You can only modify your own agency")

            # Prevent modification of is_individual
            if "is_individual" in self.initial_data:
                raise serializers.ValidationError({"is_individual": "This field cannot be modified"})

        return data


class RestrictedAgencySerializer(serializers.ModelSerializer):
    """Serializer for non-superuser recruiters"""

    class Meta:
        model = Agency
        fields = ["uuid", "agency_name", "website", "created_at", "updated_at"]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class RecruiterBasicInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20, required=False)
    primary_industry = serializers.UUIDField()
    sec_industry = serializers.UUIDField(required=False)
    linkedin = serializers.URLField()

    # def validate_phone(self, value):
    #     if value:
    #         return validate_phone_number(value)
    #     return value

    def validate_linkedin(self, value):
        """Validate LinkedIn URL format and profile type"""
        if value:
            return validate_linkedin_profile_url(value)
        raise serializers.ValidationError("LinkedIn profile URL is required")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["client", "by_user", "is_active"]

    def validate(self, data):
        """
        Validate that state belongs to the specified country
        """
        state = data.get("state")
        country = data.get("country")

        if state and country and state.country.uuid != country.uuid:
            raise serializers.ValidationError(
                {"state": f'State "{state.name}" does not belong to country "{country.name}"'}
            )

        return data

    def to_representation(self, instance):
        """
        Customize the output representation to include state and country details
        """
        data = super().to_representation(instance)
        if instance.state:
            data["state"] = {
                "id": str(instance.state.uuid),
                "name": instance.state.name,
                "code": instance.state.two_letter_code,
            }
        if instance.country:
            data["country"] = {
                "id": str(instance.country.uuid),
                "name": instance.country.name,
                "code": instance.country.two_letter_code,
            }
        return data


class RecruiterDescriptionSerializer(serializers.Serializer):
    introduction = serializers.CharField(allow_null=True, required=False)
    story = serializers.CharField(allow_null=True, required=False)


class RecruiterAgencyInfoSerializer(serializers.Serializer):
    is_individual = serializers.BooleanField()
    agency_name = serializers.CharField(max_length=255, required=False)
    make_payable_to = serializers.CharField(max_length=255)
    address = AddressSerializer(required=False)
    website = serializers.URLField(required=False)
    linkedin = serializers.URLField(required=False)

    def validate(self, data):
        if not data["is_individual"] and not data.get("agency_name"):
            raise serializers.ValidationError({"agency_name": "Agency name is required when not an individual"})
        return data


class RecruiterProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = Recruiter
        exclude = ["stripe_id"]


class RecruiterSignupResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    recruiter = serializers.CharField(allow_null=True)
    agency = serializers.CharField(allow_null=True, required=False)
    linkedin_data = serializers.JSONField(allow_null=True, required=False)

    class Meta:
        fields = ["message", "recruiter", "agency", "linkedin_data"]


# Define country-specific banking fields
COUNTRY_BANK_FIELDS = {
    "US": ["uuid", "account_name", "account_number", "routing_number", "bank_name", "bank_address", "account_address"],
    "CA": [
        "uuid",
        "account_name",
        "account_number",
        "institution_number",
        "transit_number",
        "bank_name",
        "bank_address",
        "account_address",
    ],
    "IE": ["uuid", "account_name", "account_number", "sort_code", "bank_name", "bank_address", "account_address"],
    "IE": ["uuid", "account_name", "account_number", "sort_code", "bank_name", "bank_address", "account_address"],
    "NZ": ["uuid", "account_name", "account_number", "bsb_code", "bank_name", "bank_address", "account_address"],
    "AU": ["uuid", "account_name", "account_number", "bsb_code", "bank_name", "bank_address", "account_address"],
    "default": [
        "uuid",
        "account_name",
        "account_number",
        "bank_name",
        "bank_address",
        "routing_number",
        "account_address",
    ],
}


class BankAccountSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = "__all__"
        read_only_fields = ["agency", "owner_name"]

    def get_owner_name(self, obj):
        # If agency_name is available, return it
        if obj.agency and obj.agency.agency_name:
            return obj.agency.agency_name

        # Fallback to first superuser recruiter’s name if agency_name is not available
        superuser_recruiter = obj.agency.recruiters.filter(superuser=True).first() if obj.agency else None
        if superuser_recruiter:
            return f"{superuser_recruiter.first_name} {superuser_recruiter.last_name}"

        # Return a default value if no agency name or superuser is found
        return "Owner information not available"

    def to_representation(self, instance):
        # Call the original `to_representation` to get the full data
        data = super().to_representation(instance)

        # Get the recruiter's country code
        country_code = None
        if instance.agency:
            superuser_recruiter = instance.agency.recruiters.filter(superuser=True).first()
            if superuser_recruiter and superuser_recruiter.address and superuser_recruiter.address.country:
                country_code = superuser_recruiter.address.country.two_letter_code

        # Get the fields for the country or fall back to default
        allowed_fields = COUNTRY_BANK_FIELDS.get(country_code, COUNTRY_BANK_FIELDS["default"])

        # Filter the data to include only allowed fields
        filtered_data = {
            field: value
            for field, value in data.items()
            if field in allowed_fields or field in ["owner_name", "agency"]
        }

        # Add a custom message indicating country-specific fields
        if country_code:
            country_message = f"This response is tailored for {country_code} banking fields. Other countries may have different fields."
        else:
            country_message = (
                "This response uses default banking fields as no agency or country-specific information is available."
            )

        filtered_data["message"] = country_message

        return filtered_data


# class MemberRecruiterSignupSerializer(serializers.Serializer):
#     # Basic Info
#     first_name = serializers.CharField(max_length=255)
#     last_name = serializers.CharField(max_length=255)
#     phone = serializers.CharField(max_length=20, required=False)
#     primary_industry = serializers.UUIDField()
#     sec_industry = serializers.UUIDField(required=False)
#     linkedin = serializers.URLField()

#     # Description
#     introduction = serializers.CharField(allow_null=True, required=False)
#     story = serializers.CharField(allow_null=True, required=False)

#     # Address
#     address = AddressSerializer()

#     def validate_linkedin(self, value):
#         if value:
#             return validate_linkedin_profile_url(value)
#         raise serializers.ValidationError("LinkedIn profile URL is required")

#     def create(self, validated_data):
#         user = self.context['request'].user
#         address_data = validated_data.pop('address')
#         linkedin_data = None
#         primary_industry_uuid = validated_data.pop("primary_industry", None)
#         secondary_industry_uuid = validated_data.pop("sec_industry", None)

#         # Get job category instances
#         primary_industry = JobCategory.objects.filter(uuid=primary_industry_uuid).first() if primary_industry_uuid else None
#         secondary_industry = (
#             JobCategory.objects.filter(uuid=secondary_industry_uuid).first() if secondary_industry_uuid else None
#         )
#         with transaction.atomic():
#             # Process LinkedIn data if provided
#             if validated_data.get("linkedin"):
#                 linkedin_data = process_person_linkedin_data(validated_data["linkedin"])
#                 profile_photo = linkedin_data.pop("profile_photo", None)
#             else:
#                 profile_photo = None

#             # Create address
#             address = Address.objects.create(
#                 by_user=user,
#                 **address_data,
#             )

#             # Get agency from team invite
#             agency = user.owner_profile.agency
#             recruiter_data = {
#                     'first_name': validated_data['first_name'],
#                     'last_name': validated_data['last_name'],
#                     'phone': validated_data.get('phone'),
#                     'primary_industry': primary_industry,
#                     'sec_industry': secondary_industry,
#                     'linkedin': validated_data.get('linkedin'),
#                     'introduction': validated_data.get('introduction'),
#                     'story': validated_data.get('story'),
#                     'address': address,
#                     'agency': agency,
#                     'profile_photo': profile_photo,
#                     'status': Recruiter.RecruiterStatus.ACTIVE,
#                     "approval_date": datetime.now(),
#                     'superuser': False
#                 }
#             # Create or update recruiter
#             recruiter = Recruiter.objects.create(
#                 user=user,
#                 **recruiter_data,
#             )

#             return recruiter
