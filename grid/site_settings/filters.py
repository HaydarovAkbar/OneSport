import re

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class SearchFilterBackend(BaseFilterBackend):
    """
    Custom filter backend for handling normal and quoted searches.
    """

    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get("search", None)

        if search_query:
            quoted_pattern = r'^"(.*)"$'  # Regex to match terms enclosed in double quotes
            match = re.match(quoted_pattern, search_query)

            if match:
                # Perform exact match if the search term is quoted
                exact_term = match.group(1)
                search_filter = Q()
                for field in getattr(view, "search_fields", []):
                    search_filter |= Q(**{f"{field}__iexact": exact_term})
                queryset = queryset.filter(search_filter)
            else:
                # Perform partial match for normal search terms
                search_filter = Q()
                for field in getattr(view, "search_fields", []):
                    search_filter |= Q(**{f"{field}__icontains": search_query})
                queryset = queryset.filter(search_filter)

        return queryset
