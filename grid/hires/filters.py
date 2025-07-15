import django_filters

from django.utils.timezone import now

from grid.site_settings.models import Currency

from .models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    # Filters for due_date (exact, greater than, less than)
    due_date = django_filters.DateFilter(field_name="due_date")
    due_date__gte = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date__lte = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")

    # Filter for status (exact match)
    status = django_filters.NumberFilter(field_name="status")

    # Filter for currency (exact match)
    currency = django_filters.ModelChoiceFilter(queryset=Currency.objects.all())

    # Filters for unit_price (greater than or less than)
    unit_price__gte = django_filters.NumberFilter(field_name="unit_price", lookup_expr="gte")
    unit_price__lte = django_filters.NumberFilter(field_name="unit_price", lookup_expr="lte")

    # Filter for overdue (true/false)
    overdue = django_filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model = Invoice
        fields = ["status", "due_date", "currency", "unit_price", "overdue"]

    # Custom filter for overdue (True/False)
    def filter_overdue(self, queryset, name, value):
        if value:  # If overdue is True
            return queryset.filter(status=Invoice.InvoiceStatus.DUE, due_date__lt=now())
        else:  # If overdue is False
            return queryset.exclude(status=Invoice.InvoiceStatus.DUE, due_date__lt=now())
