from rest_framework import serializers

from skin_forms.models import Cancer


class CancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancer
        read_only_fields = ["id", "skin_condition"]
        fields = [
            "id",
            "skin_condition",
            "asymmetry",
            "border",
            "color_variation",
            "diameter",
            "evolution",
        ]
