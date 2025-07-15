from django.urls import include, path
from rest_framework.routers import DefaultRouter

from grid.hires.views import HireViewSet, InvoiceViewSet, RecruiterPaymentViewSet


router = DefaultRouter()

router.register(r"recruiter-payments", RecruiterPaymentViewSet, basename="recruiter-payment")
router.register(r"hires", HireViewSet, basename="hire")
router.register(r"invoices", InvoiceViewSet, basename="invoices")

urlpatterns = [
    path("", include(router.urls)),
]
