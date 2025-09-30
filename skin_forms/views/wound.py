from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from skin_conditions.models import SkinCondition
from skin_forms.models import Wound
from skin_forms.enums.wound import (
    LesionDimension,
    DepthOfTissueInjury,
    WoundEdges,
    WoundBedTissue,
    ExudateType,
)
from skin_forms.serializers.wound import WoundSerializer, WoundDetailSerializer


class SkinConditionWoundNestedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WoundSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Wound.objects.select_related("skin_condition")
    pagination_class = None

    def get_queryset(self):
        skin_condition_id = self.kwargs.get("skin_condition_pk")
        return self.queryset.filter(skin_condition_id=skin_condition_id)

    def perform_create(self, serializer):
        skin_condition_id = self.kwargs.get("skin_condition_pk")
        skin_condition = get_object_or_404(SkinCondition, id=skin_condition_id)
        serializer.save(skin_condition=skin_condition)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WoundDetailSerializer
        return super().get_serializer_class()
