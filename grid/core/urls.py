from django.urls import path

from .views import ProxycurlCompanyView, ProxycurlPersonView


urlpatterns = [
    path("proxycurl/person/", ProxycurlPersonView.as_view(), name="proxycurl-person"),
    path("proxycurl/company/", ProxycurlCompanyView.as_view(), name="proxycurl-company"),
]
