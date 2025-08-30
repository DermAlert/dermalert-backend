from rest_framework import serializers

from profile_forms.models import FamilyVascularHistory


class FamilyVascularHistorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FamilyVascularHistory
        fields = [
            "id",
            "user",
            "family_leg_ulcers",
            "family_varicose_or_circulatory",
        ]
        read_only_fields = ["id", "user"]
