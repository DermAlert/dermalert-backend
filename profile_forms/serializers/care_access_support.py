from rest_framework import serializers

from profile_forms.models import CareAccessSupport


class CareAccessSupportSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CareAccessSupport
        fields = [
            "id",
            "user",
            "has_dressings_available",
            "has_help_at_home",
        ]
        read_only_fields = ["id", "user"]
