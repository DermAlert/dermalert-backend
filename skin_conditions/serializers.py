from rest_framework import serializers
from skin_conditions.models import SkinCondition
from skin_forms.serializers import WoundSerializer, CancerSerializer


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


class SkinConditionDetailSerializer(SkinConditionSerializer):
    wounds = WoundSerializer(many=True, read_only=True)
    cancer_forms = CancerSerializer(many=True, read_only=True)

    class Meta(SkinConditionSerializer.Meta):
        fields = SkinConditionSerializer.Meta.fields + [
            "wounds",
            "cancer_forms",
        ]
