import django_filters
from django.db.models import Q

from grid.jobs.models import Job


class JobFilter(django_filters.FilterSet):
    # General keyword search across multiple fields
    search = django_filters.CharFilter(
        method="filter_keyword",
        label="Search",
    )

    # Filter by client company name (related field)
    client_company_name = django_filters.CharFilter(
        field_name="client__company_name",
        lookup_expr="contains",
        label="Client Company Name",
        method="filter_by_client_company_name",
    )

    # Filters for location details, accessing nested location fields
    location_city = django_filters.CharFilter(
        field_name="location__city__name",
        lookup_expr="contains",
        label="City",
        method="filter_by_location_city",
    )
    location_state = django_filters.CharFilter(
        field_name="location__state__name",
        lookup_expr="contains",
        label="State",
        method="filter_by_location_state",
    )
    location_country = django_filters.CharFilter(
        field_name="location__country__name",
        lookup_expr="contains",
        label="Country",
        method="filter_by_location_country",
    )

    # Additional filters
    min_salary = django_filters.NumberFilter(
        field_name="salary_min",
        lookup_expr="gte",
        label="Minimum Salary",
        method="filter_by_min_salary",
    )
    max_salary = django_filters.NumberFilter(
        field_name="salary_max",
        lookup_expr="lte",
        label="Maximum Salary",
        method="filter_by_max_salary",
    )
    commission_percentage = django_filters.NumberFilter(
        field_name="commission_percentage",
        label="Commission Percentage",
        lookup_expr="exact",
        method="filter_by_commission_percentage",
    )
    visa_sponsorship = django_filters.BooleanFilter(
        field_name="visa_sponsorship",
        label="Visa Sponsorship",
        lookup_expr="exact",
        method="filter_by_visa_sponsorship",
    )

    class Meta:
        model = Job
        fields = [
            "search", "min_salary", "max_salary", "commission_percentage", "visa_sponsorship", "job_type",
            "position_type", "status", "client_company_name", "location_city", "location_state", "location_country"
        ]

    def filter_keyword(self, queryset, name, value):
        # Search across multiple text fields
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(about_company__icontains=value) |
            Q(must_haves__icontains=value) |
            Q(nice_to_haves__icontains=value)
        )

    def filter_by_client_company_name(self, queryset, name, value):
        # Filter by client company name
        return queryset.filter(client__company_name__icontains=value)

    def filter_by_location_city(self, queryset, name, value):
        # Filter by location city name
        return queryset.filter(location__city__icontains=value)

    def filter_by_location_state(self, queryset, name, value):
        # Filter by location state name
        return queryset.filter(location__state__name__icontains=value)

    def filter_by_location_country(self, queryset, name, value):
        # Filter by location country name
        return queryset.filter(location__country__name__icontains=value)

    def filter_by_min_salary(self, queryset, name, value):
        # Filter by minimum salary
        return queryset.filter(salary_min__gte=value)

    def filter_by_max_salary(self, queryset, name, value):
        # Filter by maximum salary
        return queryset.filter(salary_max__lte=value)

    def filter_by_commission_percentage(self, queryset, name, value):
        # Filter by commission percentage
        return queryset.filter(commission_percentage__exact=value)

    def filter_by_visa_sponsorship(self, queryset, name, value):
        # Filter by visa sponsorship
        return queryset.filter(visa_sponsorship__exact=value)
