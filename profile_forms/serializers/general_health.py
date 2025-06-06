from rest_framework import serializers
from profile_forms.models import GeneralHealth, ChronicDisease, Medicine, Allergy
from profile_forms.serializers.listed_items import (
    AllergySerializer,
    MedicineSerializer,
    ChronicDiseaseSerializer,
)


class GeneralHealthSerializer(serializers.ModelSerializer):
    chronic_diseases = ChronicDiseaseSerializer(read_only=True, many=True)
    medicines = MedicineSerializer(read_only=True, many=True)
    allergies = AllergySerializer(read_only=True, many=True)

    chronic_diseases_ids = serializers.PrimaryKeyRelatedField(
        source="chronic_diseases",
        queryset=ChronicDisease.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    medicines_ids = serializers.PrimaryKeyRelatedField(
        source="medicines",
        queryset=Medicine.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    allergies_ids = serializers.PrimaryKeyRelatedField(
        source="allergies",
        queryset=Allergy.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = GeneralHealth
        fields = [
            "id",
            "user",
            "surgeries",
            "physical_activity_frequency",
            "chronic_diseases",
            "medicines",
            "allergies",
            "chronic_diseases_ids",
            "medicines_ids",
            "allergies_ids",
        ]
        read_only_fields = ("user",)
