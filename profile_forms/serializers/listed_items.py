from rest_framework import serializers
from profile_forms.models import ChronicDisease, Medicine, Allergy


class ChronicDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicDisease
        fields = ("id", "name")


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "name")


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ("id", "name")
