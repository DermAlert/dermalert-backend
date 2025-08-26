from rest_framework import serializers
from profile_forms.models import RiskProtectiveFactors


class RiskProtectiveFactorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskProtectiveFactors
        fields = [
            "id",
            "user",
            "sun_exposure_period",
            "sun_burn",
            "uv_protection",
            "hat_use",
            "artifitial_tan",
            "checkups_frequency",
            "cancer_campaigns",
        ]
        read_only_fields = ("user",)
