from rest_framework import serializers

from profile_forms.models import ClinicalHistory


class ClinicalHistorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClinicalHistory
        fields = [
            "id",
            "user",
            "description",
            "hypertension",
            "diabetes",
            "deep_vein_thrombosis",
            "chronic_venous_insufficiency",
            "compression_stockings_use",
        ]
        read_only_fields = ["id", "user"]
