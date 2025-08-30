from rest_framework import serializers

from profile_forms.models import LifestyleRisk


class LifestyleRiskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LifestyleRisk
        fields = [
            "id",
            "user",
            "long_periods_posture",
            "leg_foot_trauma",
            "smoking",
            "physical_activity",
        ]
        read_only_fields = ["id", "user"]
