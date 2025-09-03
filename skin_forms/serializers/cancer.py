from rest_framework import serializers

from skin_forms.models import Cancer
from .image import CancerImageSerializer


class CancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancer
        read_only_fields = ["id", "skin_condition"]
        fields = [
            "id",
            "created_at",
            "skin_condition",
            "asymmetry",
            "border",
            "color_variation",
            "diameter",
            "evolution",
        ]


class CancerDetailSerializer(CancerSerializer):
    images = CancerImageSerializer(many=True, read_only=True)

    class Meta(CancerSerializer.Meta):
        fields = CancerSerializer.Meta.fields + ["images"]
