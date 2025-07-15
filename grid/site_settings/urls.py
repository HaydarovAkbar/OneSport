from django.urls import path

from grid.site_settings.views import CountryListView, StateListView, CompanySizeListView


urlpatterns = [
    path("countries/", CountryListView.as_view(), name="country-list"),
    path("states/", StateListView.as_view(), name="state-list"),
    path("company_sizes/", CompanySizeListView.as_view(), name="company-size-list"),
]
