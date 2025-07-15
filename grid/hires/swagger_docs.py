from drf_yasg import openapi


invoice_list_docs = {
    "operation_description": "List all invoices with search, filtering, pagination, and sorting. Accessible by Admin and ClientUser.",
    "manual_parameters": [
        openapi.Parameter(
            "search",
            openapi.IN_QUERY,
            description="Search (Use quotes for exact search) by client company name, about, candidate first or last name, or tax name.",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "status",
            openapi.IN_QUERY,
            description="Filter by status (1: Due, 2: Paid, 3: Void, 4: Refunded)",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "due_date",
            openapi.IN_QUERY,
            description="Exact due date filter (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
        ),
        openapi.Parameter(
            "due_date__gte",
            openapi.IN_QUERY,
            description="Filter invoices with due dates greater than or equal to (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
        ),
        openapi.Parameter(
            "due_date__lte",
            openapi.IN_QUERY,
            description="Filter invoices with due dates less than or equal to (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
        ),
        openapi.Parameter("currency", openapi.IN_QUERY, description="Filter by currency ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter(
            "unit_price__gte",
            openapi.IN_QUERY,
            description="Filter invoices with unit prices greater than or equal to",
            type=openapi.TYPE_NUMBER,
        ),
        openapi.Parameter(
            "unit_price__lte",
            openapi.IN_QUERY,
            description="Filter invoices with unit prices less than or equal to",
            type=openapi.TYPE_NUMBER,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page number for pagination.",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "page_size",
            openapi.IN_QUERY,
            description="Number of items per page (optional).",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "ordering",
            openapi.IN_QUERY,
            description="Sort results by a field. Prefix with '-' for descending order. Available fields: due_date, status, unit_price.",
            type=openapi.TYPE_STRING,
        ),
    ],
    "responses": {200: "InvoiceSerializer(many=True)"},
}
