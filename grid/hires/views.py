from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from grid.site_settings.filters import SearchFilterBackend
from grid.site_settings.models import Currency

from .filters import InvoiceFilter
from .models import Hire, Invoice, RecruiterPayment
from .serializers import HireSerializer, InvoiceSerializer, RecruiterPaymentSerializer
from .swagger_docs import invoice_list_docs


class HireViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Hire.objects.all()
    serializer_class = HireSerializer

    @swagger_auto_schema(
        operation_summary="List Hires",
        operation_description="Retrieve a list of hires based on user permissions. Accessible by admins, recruiters, and clients with relevant permissions.",
        responses={200: HireSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        # Permission-based queryset filtering
        user = request.user
        if user.is_admin:
            queryset = Hire.objects.all()
        elif hasattr(user, "recruiter"):
            if user.recruiter.is_superuser:
                queryset = Hire.objects.filter(recruiter__agency=user.recruiter.agency)
            else:
                queryset = Hire.objects.filter(recruiter=user.recruiter)

        elif hasattr(user, "clientuserprofile"):
            queryset = Hire.objects.filter(job__client=user.clientuserprofile.client)

        else:
            raise PermissionDenied("You do not have permission to view these hires.")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve Hire",
        operation_description="Retrieve a hire if the user has the necessary permissions.",
        responses={200: HireSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        hire = self.get_object()

        # Permission logic for retrieval
        user = request.user
        if user.is_admin:
            pass  # Admins can view all hires
        elif hasattr(user, "recruiter") and hire.recruiter == user.recruiter:
            pass  # Recruiters can view their own related hires
        elif hasattr(user, "clientuserprofile") and hire.job.client == user.clientuserprofile.client:
            pass  # Clients can view hires for their jobs
        else:
            raise PermissionDenied("You do not have permission to view this hire.")

        serializer = self.get_serializer(hire)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create Hire",
        operation_description="Create a hire if the user has the necessary permissions. Accessible by Superuser and Admin roles only.",
        request_body=HireSerializer,
        responses={201: HireSerializer(), 400: "Invalid data"},
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        # Only Superuser and Admin roles can create a hire
        if not (user.is_admin and user.adminuserprofile.user_type in [1, 2]):  # Superuser, Admin
            raise PermissionDenied("You do not have permission to create a hire.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update Hire Status",
        operation_description="Update a hire if the user has the necessary permissions. Only Admin roles: Superuser, Admin, Editor.",
        request_body=HireSerializer,
        responses={200: HireSerializer(), 400: "Invalid data"},
    )
    def update(self, request, *args, **kwargs):
        hire = self.get_object()
        user = request.user

        # Only Superuser, Admin, and Editor roles can update the hire status
        if not (user.is_admin and user.adminuserprofile.user_type in [1, 2, 3]):  # Superuser, Admin, Editor
            raise PermissionDenied("You do not have permission to update this hire.")

        return self.perform_update(request, hire)

    def perform_update(self, request, hire):
        """Helper function to perform update."""
        serializer = self.get_serializer(hire, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Hire",
        operation_description="Deleting hires is not allowed.",
        responses={405: "Method Not Allowed"},
    )
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Deletion not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecruiterPaymentViewSet(viewsets.ModelViewSet):
    queryset = RecruiterPayment.objects.all()
    serializer_class = RecruiterPaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List Recruiter Payments",
        operation_description="Retrieve a list of recruiter payments based on user permissions. "
        "Admins (except Viewer) can view all payments. Recruiters can view only payments "
        "related to hires they own.",
        responses={200: RecruiterPaymentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin and user.adminuserprofile.user_type != AdminUserProfile.UserType.VIEWER:
            queryset = RecruiterPayment.objects.all()
        elif hasattr(user, "recruiter"):
            queryset = RecruiterPayment.objects.filter(hire__recruiter=user.recruiter)
        else:
            raise PermissionDenied("You do not have permission to view these payments.")

        serializer = RecruiterPaymentSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve Recruiter Payment",
        operation_description="Retrieve a specific recruiter payment based on user permissions. "
        "Admins (except Viewer) and the recruiter who owns the related hire can access.",
        responses={200: RecruiterPaymentSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        user = request.user
        if user.is_admin and user.adminuserprofile.user_type != AdminUserProfile.UserType.VIEWER:
            pass
        elif hasattr(user, "recruiter") and payment.hire.recruiter == user.recruiter:
            pass
        else:
            raise PermissionDenied("You do not have permission to view this payment.")

        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create Recruiter Payment",
        operation_description="Create a recruiter payment. Accessible by Admin roles: Superadmin, Admin, Editor.",
        request_body=RecruiterPaymentSerializer,
        responses={201: RecruiterPaymentSerializer(), 400: "Invalid data"},
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        if not (
            user.is_admin
            and user.adminuserprofile.user_type
            in [
                AdminUserProfile.UserType.SUPERUSER,
                AdminUserProfile.UserType.ADMIN,
                AdminUserProfile.UserType.EDITOR,
            ]
        ):
            raise PermissionDenied("You do not have permission to create a recruiter payment.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update Recruiter Payment",
        operation_description="Update specific fields of a recruiter payment. "
        "Superadmin/Admin can edit status, due_on, and amount. "
        "Editor can only edit status and due_on.",
        request_body=RecruiterPaymentSerializer,
        responses={200: RecruiterPaymentSerializer(), 400: "Invalid data"},
    )
    def update(self, request, *args, **kwargs):
        payment = self.get_object()

        user = request.user
        if user.is_admin and user.adminuserprofile.user_type in [
            AdminUserProfile.UserType.SUPERUSER,
            AdminUserProfile.UserType.ADMIN,
        ]:
            allowed_fields = ["status", "due_on", "amount"]
        elif user.is_admin and user.adminuserprofile.user_type == AdminUserProfile.UserType.EDITOR:
            allowed_fields = ["status", "due_on"]
        else:
            raise PermissionDenied("You do not have permission to update this payment.")

        return self.perform_update(request, payment, allowed_fields)

    def perform_update(self, request, payment, allowed_fields):
        """Helper function to perform an update with restricted fields."""
        data = {field: value for field, value in request.data.items() if field in allowed_fields}
        serializer = RecruiterPaymentSerializer(payment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Recruiter Payment",
        operation_description="Deleting recruiter payments is not allowed.",
        responses={405: "Method Not Allowed"},
    )
    def destroy(self, request, *args, **kwargs):
        """
        Deny deletion of recruiter payment records.
        """
        return Response({"detail": "Deletion not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class InvoicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing invoices with custom permissions.
    """

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, SearchFilterBackend]
    filterset_class = InvoiceFilter
    pagination_class = InvoicePagination
    search_fields = [
        "client__company_name",
        "client__about",
        "hire__candidate__first_name",
        "hire__candidate__last_name",
        "tax_name",
        "invoice_code",
        "customer_name",
        "customer_address",
    ]
    ordering_fields = ["created_at", "due_date", "unit_price"]
    ordering = ["due_date"]  # default

    @swagger_auto_schema(**invoice_list_docs)
    def list(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, "adminuserprofile") and user.adminuserprofile.user_type in [
            1,
            2,
            5,
        ]:  # SuperAdmin, Admin, Accountant have access to all invoices
            queryset = self.queryset
        elif hasattr(user, "clientuserprofile") and user.clientuserprofile.client.user_type in [
            1,
            2,
        ]:  # ClientUser Superuser or Admin
            # ClientUsers can access only their own invoices
            queryset = self.queryset.filter(client=user.clientuserprofile.client)
        else:
            # Recruiters and unauthorized users are denied
            return Response(
                {"detail": "You do not have permission to view invoices."}, status=status.HTTP_403_FORBIDDEN
            )

        # Apply ordering and pagination
        queryset = self.filter_queryset(queryset)  # Apply filters and ordering
        page = self.paginate_queryset(queryset)  # Paginate the queryset

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Return paginated response

        # If pagination is not used, return all data
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a specific invoice. Accessible by Admin (SuperAdmin, Admin, Accountant) and ClientUser with related client where client is Superuser or Admin.",
        responses={200: InvoiceSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        invoice = self.get_object()

        if hasattr(user, "adminuserprofile") and user.adminuserprofile.user_type in [
            1,
            2,
            5,
        ]:  # SuperAdmin, Admin, Accountant
            # Admins have access
            pass
        elif (
            hasattr(user, "clientuserprofile")
            and invoice.client == user.clientuserprofile.client
            and user.clientuserprofile.client.user_type in [1, 2]
        ):  # ClientUser with permissions
            # ClientUser can access their own related invoice
            pass
        else:
            # Recruiters and unauthorized users are denied
            return Response(
                {"detail": "You do not have permission to view this invoice."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new invoice. Accessible by Admin (SuperAdmin, Admin, Accountant) only.",
        responses={201: InvoiceSerializer()},
        request_body=InvoiceSerializer,
    )
    def create(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, "adminuserprofile") and user.adminuserprofile.user_type in [
            1,
            2,
            5,
        ]:  # SuperAdmin, Admin, Accountant
            # Allowed to create
            return super().create(request, *args, **kwargs)
        else:
            # ClientUser and Recruiter are denied
            return Response(
                {"detail": "You do not have permission to create invoices."}, status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_description="Update an existing invoice. Accessible by Admin (SuperAdmin, Admin) only.",
        responses={200: InvoiceSerializer()},
        request_body=InvoiceSerializer,
    )
    def update(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, "adminuserprofile") and user.adminuserprofile.user_type in [1, 2]:  # SuperAdmin, Admin
            # Allowed to update
            return super().update(request, *args, **kwargs)
        else:
            # ClientUser and Recruiter are denied
            return Response(
                {"detail": "You do not have permission to update invoices."}, status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_description="Delete an invoice. This operation is disabled.",
        responses={403: "This operation is not permitted."},
    )
    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Deleting invoices is not permitted."}, status=status.HTTP_403_FORBIDDEN)
