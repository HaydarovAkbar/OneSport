from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from grid.site_settings.models import CompanySize, Country, State
from grid.site_settings.serializers import (
    CompanySizeSerializer,
    CountrySerializer,
    StateSerializer,
)


class CountryListView(ListAPIView):
    serializer_class = CountrySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["priority", "name"]
    ordering = ["priority", "name"]

    def get_queryset(self):
        return Country.objects.filter(is_active=True)

    @swagger_auto_schema(
        operation_description="Get list of all active countries",
        operation_summary="List Countries",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by fields (prefix with '-' for descending). Example: priority,-name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: CountrySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StateListView(ListAPIView):
    serializer_class = StateSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = State.objects.filter(is_active=True)
        country_id = self.request.query_params.get("country_id")
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset

    @swagger_auto_schema(
        operation_description="Get list of all active states. Can be filtered by country_id",
        operation_summary="List States",
        manual_parameters=[
            openapi.Parameter(
                "country_id",
                openapi.IN_QUERY,
                description="Filter states by country UUID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by fields (prefix with '-' for descending). Example: -name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: StateSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompanySizeListView(ListAPIView):
    serializer_class = CompanySizeSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["priority", "name"]
    ordering = ["priority", "name"]

    def get_queryset(self):
        return CompanySize.objects.all()

    @swagger_auto_schema(
        operation_description="Get list of all active company sizes",
        operation_summary="List Company Sizes",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by fields (prefix with '-' for descending). Example: priority,-name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: CompanySizeSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
