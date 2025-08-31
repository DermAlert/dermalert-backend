from rest_framework import serializers
from skin_conditions.models import SkinCondition
from skin_forms.serializers import WoundDetailSerializer, CancerDetailSerializer


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
    wounds = WoundDetailSerializer(many=True, read_only=True)
    cancer_forms = CancerDetailSerializer(many=True, read_only=True)

    class Meta(SkinConditionSerializer.Meta):
        fields = SkinConditionSerializer.Meta.fields + [
            "wounds",
            "cancer_forms",
        ]
