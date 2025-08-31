from rest_framework import serializers

from skin_forms.models import WoundImage, CancerImage


class WoundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundImage
        read_only_fields = ["id", "wound"]
        fields = ["id", "wound", "image"]


class CancerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerImage
        read_only_fields = ["id", "cancer"]
        fields = ["id", "cancer", "image"]
