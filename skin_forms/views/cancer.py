from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets

from skin_forms.models import Cancer
from skin_forms.serializers.cancer import CancerSerializer, CancerDetailSerializer
from skin_conditions.models import SkinCondition


class SkinConditionCancerNestedViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CancerSerializer
    queryset = Cancer.objects.select_related("skin_condition")
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        skin_condition_id = self.kwargs.get("skin_condition_pk")
        return self.queryset.filter(skin_condition_id=skin_condition_id)

    def perform_create(self, serializer):
        sc_id = self.kwargs.get("skin_condition_pk")
        sc = get_object_or_404(SkinCondition, id=sc_id)
        serializer.save(skin_condition=sc)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CancerDetailSerializer
        return super().get_serializer_class()
