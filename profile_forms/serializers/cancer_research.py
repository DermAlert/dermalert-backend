from rest_framework import serializers
from profile_forms.models import CancerResearch


class CancerResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerResearch
        fields = [
            "id",
            "user",
            "suspicious_moles",
            "bleed_itch",
            "how_long",
            "lesion_aspect",
            "doctor_assistance",
            "diagnosis",
        ]
        read_only_fields = ("user",)
