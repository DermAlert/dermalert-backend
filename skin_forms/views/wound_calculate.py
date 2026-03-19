from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from typing import Any, Mapping, cast

from skin_forms.models import Wound
from skin_forms.enums.wound import (
    LesionDimension,
    DepthOfTissueInjury,
    WoundEdges,
    WoundBedTissue,
    ExudateType,
)
from skin_forms.serializers.wound import WoundSerializer
from accounts.permissions import ClinicalAccessPermission


class WoundCalculateView(APIView):
    permission_classes = [permissions.IsAuthenticated, ClinicalAccessPermission]

    @swagger_auto_schema(
        request_body=WoundSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "breakdown": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "lesion_dimension_points": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "depth_points": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "edges_points": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "bed_tissue_points": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "exudate_points": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "infection_flags_points": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                        },
                    ),
                    "dimension_area_cm2": openapi.Schema(type=openapi.TYPE_NUMBER),
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):
        """POST /api/v1/wounds/calculate/
        Valida os campos, calcula o total_score e retorna sem persistir.
        """
        serializer = WoundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated = cast(Mapping[str, Any], serializer.validated_data)
        data: dict[str, Any] = dict(validated)
        temp = Wound(**data)

        height_cm = float(temp.height_mm) / 10.0
        width_cm = float(temp.width_mm) / 10.0
        item1 = LesionDimension.get_points(height_cm, width_cm)
        item2 = DepthOfTissueInjury.get_points(temp.depth_of_tissue_injury)
        item3 = WoundEdges.get_points(temp.wound_edges)
        item4 = WoundBedTissue.get_points(temp.wound_bed_tissue)
        item5 = ExudateType.get_points(temp.exudate_type)
        item6 = temp.get_item6_points()
        total = temp.get_total_score()

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
