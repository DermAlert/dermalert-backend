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

    @action(detail=False, methods=["post"], url_path="calculate")
    def calculate(self, request, *args, **kwargs):
        """POST /patients/{user_pk}/skin-conditions/{skin_condition_pk}/wounds/calculate/
        Valida os campos, calcula o total_score e retorna sem persistir.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        temp = Wound(**serializer.validated_data)

        height_cm = float(temp.height_mm) / 10.0
        width_cm = float(temp.width_mm) / 10.0
        item1 = LesionDimension.get_points(height_cm, width_cm)
        item2 = DepthOfTissueInjury.get_points(temp.depth_of_tissue_injury)
        item3 = WoundEdges.get_points(temp.wound_edges)
        item4 = WoundBedTissue.get_points(temp.wound_bed_tissue)
        item5 = ExudateType.get_points(temp.exudate_type)
        item6 = temp.get_item6_points()
        total = item1 + item2 + item3 + item4 + item5 + item6

        return Response(
            {
                "total_score": total,
                "breakdown": {
                    "lesion_dimension_points": item1,
                    "depth_points": item2,
                    "edges_points": item3,
                    "bed_tissue_points": item4,
                    "exudate_points": item5,
                    "infection_flags_points": item6,
                },
                "dimension_area_cm2": height_cm * width_cm,
            }
        )
