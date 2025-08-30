from rest_framework import serializers
from skin_conditions.models import SkinCondition


class SkinConditionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SkinCondition
        fields = [
            "id",
            "user",
            "location",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
