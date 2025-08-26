from rest_framework import serializers
from profile_forms.models import Phototype


class PhototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phototype
        fields = [
            "id",
            "user",
            "skin_color",
            "eyes_color",
            "hair_color",
            "freckles",
            "sun_exposed",
            "tanned_skin",
            "sun_sensitive_skin",
            "phototype",
            "score",
        ]
        read_only_fields = ("user", "phototype", "score")
