from rest_framework import serializers

from profile_forms.models import CurrentUlcerInfo


class CurrentUlcerInfoSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CurrentUlcerInfo
        fields = [
            "id",
            "user",
            "how_long",
            "treated_elsewhere",
            "used_antibiotics",
        ]
        read_only_fields = ["id", "user"]
