from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets

from skin_forms.models import Wound, WoundImage
from skin_forms.serializers import WoundImageSerializer


class WoundImageNestedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WoundImageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = WoundImage.objects.select_related("wound")
    pagination_class = None

    def get_queryset(self):
        wound_id = self.kwargs.get("wound_pk")
        return self.queryset.filter(wound_id=wound_id)

    def perform_create(self, serializer):
        wound_id = self.kwargs.get("wound_pk")
        wound = get_object_or_404(Wound, id=wound_id)
        serializer.save(wound=wound)
