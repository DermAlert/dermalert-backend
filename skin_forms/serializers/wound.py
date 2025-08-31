from rest_framework import serializers

from skin_forms.models import Wound
from .image import WoundImageSerializer


class WoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wound
        read_only_fields = ["id", "total_score", "skin_condition"]
        fields = [
            "id",
            "skin_condition",
            "height_mm",
            "width_mm",
            "wound_edges",
            "wound_bed_tissue",
            "depth_of_tissue_injury",
            "exudate_type",
            "increased_pain",
            "perilesional_erythema",
            "perilesional_edema",
            "heat_or_warm_skin",
            "increased_exudate",
            "purulent_exudate",
            "friable_tissue",
            "stagnant_wound",
            "biofilm_compatible_tissue",
            "odor",
            "hypergranulation",
            "wound_size_increase",
            "satallite_lesions",
            "grayish_wound_bed",
            "total_score",
        ]


class WoundDetailSerializer(WoundSerializer):
    images = WoundImageSerializer(many=True, read_only=True)

    class Meta(WoundSerializer.Meta):
        fields = WoundSerializer.Meta.fields + ["images"]
