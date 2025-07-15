from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JobAttachmentUploadView, \
    JobAttachmentDeleteView, JobViewSet


router = DefaultRouter()

router.register(r"", JobViewSet, basename="job")


urlpatterns = [
    path("attachments/upload/", JobAttachmentUploadView.as_view(), name="attachment-upload"),
    path("attachments/<uuid:uuid>/delete/", JobAttachmentDeleteView.as_view(), name="attachment-delete"),
]

urlpatterns += router.urls
