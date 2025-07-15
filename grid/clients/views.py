from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from grid.admins.models import AdminUserProfile
from grid.clients.models import Address, Client, ClientUserProfile, Industry
from grid.clients.serializers import (
    AddressSerializer,
    ClientBasicInfoSerializer,
    ClientCompanyInfoSerializer,
    ClientSerializer,
    ClientSignupResponseSerializer,
    ClientUserProfileSerializer,
    IndustrySerializer,
)
from grid.clients.utils import get_company_size_range
from grid.core.permissions import (
    IsAdmin,
    IsAdminAdmin,
    IsAdminEditor,
    IsAdminSuperAdmin,
    IsClient,
    IsClientAdmin,
    IsClientSuperAdmin,
    IsRecruiter,
)
from grid.core.viewsets import NoCreateViewSet
from grid.recruiters.utils import download_image
from grid.site_settings.models import Country, State


class IndustryListView(ListAPIView):
    serializer_class = IndustrySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["priority", "name"]
    ordering = ["priority", "name"]

    def get_queryset(self):
        return Industry.objects.active()

    @swagger_auto_schema(
        operation_description="Get list of all active industries",
        operation_summary="List Industries",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by fields (prefix with '-' for descending). Example: priority,-name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: IndustrySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ClientViewSet(NoCreateViewSet):
    serializer_class = ClientSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.active()

        if user.is_admin:
            return queryset
        elif hasattr(user, "clientuserprofile"):
            return queryset.filter(uuid=user.clientuserprofile.client.uuid)
        return Client.objects.none()

    def check_permissions(self, request):
        super().check_permissions(request)

        # Additional permission checks for modifications
        if request.method in ["PUT", "PATCH"]:
            user = request.user

            if user.is_admin:
                # Check if admin has proper role
                admin_roles = ["SUPERADMIN", "ADMIN", "EDITOR"]
                if not hasattr(user, "adminuserprofile") or user.adminuserprofile.user_type not in admin_roles:
                    raise PermissionDenied("Only specific admin roles can modify clients")

            elif hasattr(user, "clientuserprofile"):
                # Check if client user has proper role for editing
                if user.clientuserprofile.user_type not in [
                    ClientUserProfile.UserType.SUPERUSER,
                    ClientUserProfile.UserType.ADMIN,
                ]:
                    raise PermissionDenied("Only superadmin and admin users can modify client details")

    @swagger_auto_schema(
        operation_description="List clients associated with the authenticated user",
        responses={200: ClientSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve a specific client", responses={200: ClientSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a client", request_body=ClientSerializer, responses={200: ClientSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a client",
        request_body=ClientSerializer,
        responses={200: ClientSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class ClientUserProfileViewSet(NoCreateViewSet):
    serializer_class = ClientUserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ClientUserProfile.objects.select_related("user", "client").active()

        if user.is_admin:
            return queryset
        return queryset.filter(user=user)

    @swagger_auto_schema(
        operation_description="List client user profiles",
        responses={200: ClientUserProfileSerializer(many=True), 403: "Permission denied"},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve client user profile",
        responses={200: ClientUserProfileSerializer(), 403: "Permission denied", 404: "Not found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a client profile",
        request_body=ClientUserProfileSerializer,
        responses={200: ClientUserProfileSerializer(), 400: "Invalid data", 403: "Permission denied", 404: "Not found"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a client profile",
        request_body=ClientUserProfileSerializer,
        responses={200: ClientUserProfileSerializer(), 400: "Invalid data", 403: "Permission denied", 404: "Not found"},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class ClientSignupViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsClient]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""

        if self.action == "basic_info":
            return ClientBasicInfoSerializer
        elif self.action == "company_info":
            return ClientCompanyInfoSerializer
        else:
            return ClientSignupResponseSerializer

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def basic_info(self, request):
        """Handle basic info submission for client signup"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        # Create client with temporary name
        if user.is_team_member:
            client = user.owner_profile
        else:
            client = Client.objects.create(
                company_name="Company Name Pending",
                linkedin=serializer.validated_data.get("company_linkedin"),
                status=Client.Status.PENDING_SIGNUP,
            )

        # Create client user profile
        user_type = None
        if user.is_team_member:
            user_type = ClientUserProfile.UserType[user.team_invite.data["user_type"]]
        else:
            user_type = ClientUserProfile.UserType.SUPERUSER  # First user is superuser

        profile = ClientUserProfile.objects.create(
            user=request.user,
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            phone=serializer.validated_data.get("phone"),
            job_title=serializer.validated_data.get("job_title"),
            client=client,
            user_type=user_type,
        )

        response_data = {
            "message": "Basic information saved successfully",
            "client": client.uuid,
            "client_profile": profile.uuid,
        }

        response_serializer = ClientSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def company_info(self, request):
        """Handle company information submission"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get client and profile in one query
        profile = get_object_or_404(ClientUserProfile.objects.select_related("client"), user=request.user)
        client = profile.client

        # Get company size range from LinkedIn employee count
        company_size, linkedin_company_size = get_company_size_range(serializer.validated_data["linkedin_company_size"])

        # Update client information
        client.company_name = serializer.validated_data["company_name"]
        client.company_size = company_size
        client.linkedin_company_size = linkedin_company_size
        client.industry = serializer.validated_data["industry"]

        if "website" in serializer.validated_data:
            client.website = serializer.validated_data.get("website")

        # Handle logo download
        logo_url = serializer.validated_data.get("logo_url")

        if logo_url:
            logo_image = download_image(logo_url)
            if logo_image:
                client.logo = logo_image

        # Handle profile picture download
        profile_pic_url = serializer.validated_data.get("profile_pic_url")
        if profile_pic_url:
            profile_image = download_image(profile_pic_url)
            if profile_image:
                profile.profile_photo = profile_image
                profile.save(update_fields=["profile_photo", "updated_at"])

        client.status = Client.Status.PENDING_APPROVAL
        client.save()

        # Create address
        address_data = serializer.validated_data.get("address")

        address = Address.objects.create(**address_data, client=client, by_user=request.user)

        client.country = address.country
        client.save(update_fields=["country", "updated_at"])

        response_data = {
            "message": "Company information saved successfully",
            "client": str(client.uuid),
            "client_profile": str(profile.uuid),
            "address": str(address.uuid),
        }

        response_serializer = ClientSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all addresses",
        operation_description="Retrieve a list of all addresses.",
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if request.user.role == "RECRUITER":
            # Limit to the recruiter's own address
            queryset = queryset.filter(uuid=request.user.recruiter.address.uuid)

        elif request.user.role == "CLIENT":
            # Limit to addresses belonging to the client's company
            queryset = queryset.filter(client=request.user.clientuserprofile.client)

        elif request.user.role == "ADMIN":
            pass

        self.queryset = queryset
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new address",
        operation_description="Create a new address for the authenticated client.",
        responses={201: AddressSerializer},
    )
    def create(self, request, *args, **kwargs):
        # Restrict recruiters from creating addresses
        if request.user.role == "RECRUITER":
            raise PermissionDenied("Recruiters are not allowed to create addresses.")

        # Allow clients and admins to create addresses
        if request.user.role == "CLIENT":
            pass

        if request.user.role == "ADMIN":
            admin_profile = AdminUserProfile.objects.filter(user=request.user).first()

            # Raise an exception if admin_profile is None
            if not admin_profile:
                raise PermissionDenied("Admin profile not found for this user.")

            # Check if the user has the required sub-role
            if admin_profile.user_type not in [
                AdminUserProfile.UserType.SUPERADMIN,
                AdminUserProfile.UserType.ADMIN,
                AdminUserProfile.UserType.EDITOR,
            ]:
                raise PermissionDenied("You do not have permission to update this address.")

            # Proceed with creation if admin has the required sub-role
            return super().create(request, *args, **kwargs)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific address",
        operation_description="Retrieve an address by ID.",
        responses={200: AddressSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        address = self.get_object()  # Get the address instance to be retrieved

        # Restrict recruiter to only retrieve their own address
        if request.user.role == "RECRUITER":
            if address != request.user.recruiter.address:
                raise PermissionDenied("You do not have permission to view this address.")

        # Restrict client user to only retrieve addresses belonging to their client
        elif request.user.role == "CLIENT":
            if address.client != request.user.clientuserprofile.client:
                raise PermissionDenied("You do not have permission to view this address.")

        # Admins can retrieve any address without restriction
        elif request.user.role == "ADMIN":
            pass

        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an address",
        operation_description=(
            "Update an existing address. Only Admin, Client, and Recruiter " "have permissions to update."
        ),
        responses={200: AddressSerializer},
    )
    def update(self, request, *args, **kwargs):
        # Assuming `Address` is the model you're working with
        try:
            # Retrieve the address instance by primary key or other unique identifier
            address = Address.objects.get(pk=kwargs.get("pk"))

        except Address.DoesNotExist:
            raise NotFound("Address not found.")

        if request.user.role == "RECRUITER":
            if address != request.user.recruiter.address:
                raise PermissionDenied("You do not have permission to update this address.")

                self.permission_classes = [IsRecruiter]

        elif request.user.role == "CLIENT":
            if address.client != request.user.clientuserprofile.client:
                raise PermissionDenied("You do not have permission to update this address.")

                self.permission_classes = [IsClient]

        elif request.user.role == "ADMIN":
            admin_profile = AdminUserProfile.objects.filter(user=request.user).first()

            # Raise an exception if admin_profile is None
            if not admin_profile:
                raise PermissionDenied("Admin profile not found for this user.")

            # Check if the user has the required sub-role
            if admin_profile.user_type not in [
                AdminUserProfile.UserType.SUPERADMIN,
                AdminUserProfile.UserType.ADMIN,
                AdminUserProfile.UserType.EDITOR,
            ]:
                raise PermissionDenied("You do not have permission to update this address.")

        return super().update(request, *args, **kwargs)
