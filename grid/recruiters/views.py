from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from grid.admins.models import AdminUserProfile
from grid.clients.models import Address
from grid.core.permissions import IsRecruiter
from grid.core.viewsets import NoCreateViewSet
from grid.recruiters.models import Agency, BankAccount, JobCategory, Recruiter
from grid.recruiters.serializers import (  # MemberRecruiterSignupSerializer,
    AddressSerializer,
    AgencySerializer,
    BankAccountSerializer,
    JobCategorySerializer,
    RecruiterAgencyInfoSerializer,
    RecruiterBasicInfoSerializer,
    RecruiterDescriptionSerializer,
    RecruiterSerializer,
    RecruiterSignupResponseSerializer,
    RestrictedAgencySerializer,
    RestrictedRecruiterSerializer,
)
from grid.recruiters.utils import (
    create_agency_and_address_from_info,
    create_recruiter_from_basic_info,
    process_person_linkedin_data,
)
from grid.users.permissions import IsTeamMember


class JobCategoryListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobCategorySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["priority", "name"]
    ordering = ["priority", "name"]

    def get_queryset(self):
        return JobCategory.objects.active()

    @swagger_auto_schema(
        operation_description="Get list of all active job categories",
        operation_summary="List Job Categories",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by fields (prefix with '-' for descending). Example: priority,-name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: JobCategorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RecruiterViewSet(NoCreateViewSet):
    serializer_class = RecruiterSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Recruiter.objects.active()

        if user.is_admin:
            return queryset
        return queryset.filter(user=user)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_recruiter and not user.recruiter.superuser:
            return RestrictedRecruiterSerializer
        return RecruiterSerializer

    @swagger_auto_schema(
        operation_description="List recruiter profiles for the authenticated user",
        responses={200: RecruiterSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific recruiter profile", responses={200: RecruiterSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a recruiter profile",
        request_body=RecruiterSerializer,
        responses={200: RecruiterSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a recruiter profile",
        request_body=RecruiterSerializer,
        responses={200: RecruiterSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AgencyViewSet(NoCreateViewSet):
    serializer_class = AgencySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Agency.objects.select_related().active()

        if user.is_admin:
            return queryset
        elif user.is_recruiter and hasattr(user, "recruiter"):
            # Show agency to all recruiters who belong to the same agency
            return queryset.filter(uuid=user.recruiter.agency_id)
        return Agency.objects.none()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_recruiter and not user.recruiter.superuser:
            return RestrictedAgencySerializer
        return AgencySerializer

    def check_permissions(self, request):
        super().check_permissions(request)

        # Additional permission checks for modifications
        if request.method in ["PUT", "PATCH"]:
            user = request.user

            if user.is_admin:
                # Check if admin has proper role
                admin_roles = [1, 2, 3]
                if not hasattr(user, "adminuserprofile") or user.adminuserprofile.user_type not in admin_roles:
                    raise PermissionDenied("Only specific admin roles can modify agencies")

            elif user.is_recruiter:
                # Check if recruiter is superuser
                if not user.recruiter.superuser:
                    raise PermissionDenied("Only superuser recruiters can modify agencies")

    @swagger_auto_schema(
        operation_description="List agencies", responses={200: AgencySerializer(many=True), 403: "Permission denied"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve agency details",
        responses={200: AgencySerializer(), 403: "Permission denied", 404: "Not found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an agency", request_body=AgencySerializer, responses={200: AgencySerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an agency",
        request_body=AgencySerializer,
        responses={200: AgencySerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class RecruiterSignupViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsRecruiter]

    ACTION_SERIALIZER = {
        "basic_info": RecruiterBasicInfoSerializer,
        "agency_info": RecruiterAgencyInfoSerializer,
        "description_info": RecruiterDescriptionSerializer,
        "address_info": AddressSerializer,
    }

    def get_serializer_class(self):
        return self.ACTION_SERIALIZER.get(self.action)

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def basic_info(self, request):
        """
        Handle basic info submission for recruiter signup
        Returns standardized response with next steps and profile info
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        linkedin_data = None
        if serializer.validated_data.get("linkedin"):
            linkedin_data = process_person_linkedin_data(serializer.validated_data["linkedin"])

        profile_picture = linkedin_data.pop("profile_photo")

        recruiter = create_recruiter_from_basic_info(
            user=request.user, profile_photo=profile_picture, basic_info_data=serializer.validated_data
        )

        # Prepare response data
        response_data = {
            "message": "Basic information saved successfully",
            "recruiter": str(recruiter.uuid),
            "agency": None,
            "linkedin_data": linkedin_data,
        }

        response_serializer = RecruiterSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        print(response_serializer.validated_data)

        return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def agency_info(self, request):
        """Handle agency info submission"""
        if request.user.is_team_member:
            return Response(
                {"error": "member users cannot create agency information"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recruiter = get_object_or_404(Recruiter, user=request.user)

        # Create agency and address
        agency, address = create_agency_and_address_from_info(
            agency_info_data=serializer.validated_data, user=request.user
        )

        # Update recruiter
        recruiter.agency = agency
        recruiter.address = address
        recruiter.save(update_fields=["agency", "address", "updated_at"])

        # Prepare response
        response_data = {
            "message": "Agency info saved",
            "recruiter": str(recruiter.uuid),
            "agency": str(agency.uuid) if agency else None,
            "linkedin_data": None,
        }

        response_serializer = RecruiterSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="description")
    def description_info(self, request):
        """Handle optional description submission"""
        recruiter = get_object_or_404(Recruiter, user=request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recruiter.introduction = serializer.validated_data.get("introduction")
        recruiter.story = serializer.validated_data.get("story")
        recruiter.status = (
            Recruiter.RecruiterStatus.ACTIVE
            if request.user.is_team_member
            else Recruiter.RecruiterStatus.PENDING_APPROVAL
        )

        recruiter.save(update_fields=["introduction", "story", "status", "updated_at"])

        response_data = {
            "message": "Profile description updated successfully",
            "recruiter": str(recruiter.uuid),
            "agency": str(recruiter.agency.uuid) if recruiter.agency else None,
        }

        response_serializer = RecruiterSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update recruiter address",
        operation_description="Update address information for team member recruiters",
        request_body=AddressSerializer,
        responses={
            201: RecruiterSignupResponseSerializer(),
            403: "Only team members can use this endpoint",
            404: "Recruiter profile not found",
        },
    )
    @transaction.atomic
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsRecruiter, IsTeamMember])
    def address_info(self, request):
        """Handle address submission for team members"""
        recruiter = get_object_or_404(Recruiter, user=request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create new address
        address = Address.objects.create(by_user=request.user, **serializer.validated_data)

        # Update recruiter's address
        recruiter.address = address
        recruiter.save(update_fields=["address", "updated_at"])

        response_data = {
            "message": "Address information updated successfully",
            "recruiter": str(recruiter.uuid),
            "agency": str(recruiter.agency.uuid) if recruiter.agency else None,
        }

        response_serializer = RecruiterSignupResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.validated_data, status=status.HTTP_201_CREATED)


class BankAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve Bank Account",
        operation_description="Retrieve a bank account if the user has the necessary permissions. Accessible by recruiters with agency access and certain admin roles.",
        responses={200: BankAccountSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        bank_account = self.get_object()

        # Permission logic for retrieving
        if hasattr(request.user, "recruiter") and request.user.recruiter.superuser:
            if request.user.recruiter.agency == bank_account.agency:
                serializer = self.get_serializer(bank_account)
                return Response(serializer.data)

        elif hasattr(request.user, "adminuserprofile") and request.user.adminuserprofile.user_type in [
            AdminUserProfile.UserType.SUPERUSER,
            AdminUserProfile.UserType.ADMIN,
            AdminUserProfile.UserType.ACCOUNTANT,
        ]:
            serializer = self.get_serializer(bank_account)
            return Response(serializer.data)

        raise PermissionDenied("You do not have permission to view this bank account.")

    @swagger_auto_schema(
        operation_summary="Create Bank Account",
        operation_description="Create a bank account if the user has the necessary permissions. Accessible by recruiters with agency access.",
        request_body=BankAccountSerializer,
        responses={201: BankAccountSerializer(), 400: "Invalid data"},
    )
    def create(self, request, *args, **kwargs):
        # Permission logic for creating
        if hasattr(request.user, "recruiter") and request.user.recruiter.superuser:
            if request.user.recruiter.agency is not None:
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(agency=request.user.recruiter.agency)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raise PermissionDenied("You do not have permission to create a bank account.")

    @swagger_auto_schema(
        operation_summary="Update Bank Account",
        operation_description="Update a bank account if the user has the necessary permissions.",
        request_body=BankAccountSerializer,
        responses={200: BankAccountSerializer(), 400: "Invalid data"},
    )
    def update(self, request, *args, **kwargs):
        bank_account = self.get_object()

        # Permission logic for Recruiters with agency access
        if hasattr(request.user, "recruiter") and request.user.recruiter.superuser:
            if request.user.recruiter.agency == bank_account.agency:
                return self.perform_update(request, bank_account)

        # Permission logic for AdminSuperAdmin
        if (
            hasattr(request.user, "adminuserprofile")
            and request.user.adminuserprofile.user_type == AdminUserProfile.UserType.SUPERUSER
        ):
            return self.perform_update(request, bank_account)

        # Raise permission denied if no conditions are met
        raise PermissionDenied("You do not have permission to update this bank account.")

    def perform_update(self, request, bank_account):
        """Helper function to perform update."""
        serializer = self.get_serializer(bank_account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Bank Account",
        operation_description="Deleting bank accounts is not allowed.",
        responses={405: "Method Not Allowed"},
    )
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Deletion not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class MemberRecruiterSignupView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated, IsRecruiter]
#     serializer_class = MemberRecruiterSignupSerializer

#     @swagger_auto_schema(
#         operation_summary="Member Recruiter Signup",
#         operation_description="Complete signup process for team member recruiters",
#         request_body=MemberRecruiterSignupSerializer,
#         responses={
#             201: openapi.Response(
#                 description="Signup successful",
#                 examples={
#                     "application/json": {
#                         "message": "Profile created successfully",
#                         "recruiter": "uuid-here",
#                         "agency": "agency-uuid-here"
#                     }
#                 }
#             ),
#             400: "Invalid data",
#             403: "Not a team member"
#         }
#     )
#     def create(self, request, *args, **kwargs):
#         if not request.user.is_team_member:
#             raise PermissionDenied("Only team members can use this endpoint")

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         recruiter = serializer.save()

#         response_data = {
#             "message": "Profile created successfully",
#             "recruiter": str(recruiter.uuid),
#             "agency": str(recruiter.agency.uuid) if recruiter.agency else None
#         }

#         return Response(response_data, status=status.HTTP_201_CREATED)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context
