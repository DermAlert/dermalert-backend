from rest_framework import serializers
from profile_forms.models import ChronicDisease, Medicine, Allergy


class ChronicDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicDisease
        fields = ("id", "name")
        # Disable UniqueValidator to allow nested writes to reuse existing records by name
        extra_kwargs = {
            "name": {"validators": []}
        }


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "name")
        # Disable UniqueValidator to allow nested writes to reuse existing records by name
        extra_kwargs = {
            "name": {"validators": []}
        }


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ("id", "name")
        # Disable UniqueValidator to allow nested writes to reuse existing records by name
        extra_kwargs = {
            "name": {"validators": []}
        }
