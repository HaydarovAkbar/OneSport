from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated


class NoCreateViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for all operations except create"""

    permission_classes = [IsAuthenticated]
