from django.urls import include, path
from rest_framework.routers import DefaultRouter

from grid.clients.views import (
    AddressViewSet,
    ClientSignupViewSet,
    ClientUserProfileViewSet,
    ClientViewSet,
    IndustryListView,
)


router = DefaultRouter()

router.register(r"clients", ClientViewSet, basename="client")
router.register(r"client-profiles", ClientUserProfileViewSet, basename="client-profile")
router.register(r"signup", ClientSignupViewSet, basename="client-signup")
router.register(r"addresses", AddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("industries/", IndustryListView.as_view(), name="industry-list"),
]
