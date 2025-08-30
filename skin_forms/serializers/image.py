from rest_framework import serializers

from skin_forms.models import WoundImage


class WoundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundImage
        read_only_fields = ["id", "wound"]
        fields = ["id", "wound", "image"]
