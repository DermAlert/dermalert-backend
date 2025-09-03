from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets

from skin_forms.models import Cancer, CancerImage
from skin_forms.serializers import CancerImageSerializer


class CancerImageNestedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CancerImageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CancerImage.objects.select_related("cancer")
    pagination_class = None

    def get_queryset(self):
        cancer_id = self.kwargs.get("cancer_pk")
        return self.queryset.filter(cancer_id=cancer_id)

    def perform_create(self, serializer):
        cancer_id = self.kwargs.get("cancer_pk")
        cancer = get_object_or_404(Cancer, id=cancer_id)
        serializer.save(cancer=cancer)
