from rest_framework import serializers
from profile_forms.models import GeneralHealth, ChronicDisease, Medicine, Allergy
from profile_forms.serializers.listed_items import (
    AllergySerializer,
    MedicineSerializer,
    ChronicDiseaseSerializer,
)


class GeneralHealthSerializer(serializers.ModelSerializer):
    chronic_diseases = ChronicDiseaseSerializer(many=True, required=False)
    medicines = MedicineSerializer(many=True, required=False)
    allergies = AllergySerializer(many=True, required=False)

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
        ]
        read_only_fields = ("user",)

    def create(self, validated_data):
        chronic_diseases_data = validated_data.pop('chronic_diseases', [])
        medicines_data = validated_data.pop('medicines', [])
        allergies_data = validated_data.pop('allergies', [])
        
        general_health = GeneralHealth.objects.create(**validated_data)
        
        # Handle chronic diseases
        for chronic_disease_data in chronic_diseases_data:
            chronic_disease, _ = ChronicDisease.objects.get_or_create(
                name=chronic_disease_data['name']
            )
            general_health.chronic_diseases.add(chronic_disease)
        
        # Handle medicines
        for medicine_data in medicines_data:
            medicine, _ = Medicine.objects.get_or_create(
                name=medicine_data['name']
            )
            general_health.medicines.add(medicine)
        
        # Handle allergies
        for allergy_data in allergies_data:
            allergy, _ = Allergy.objects.get_or_create(
                name=allergy_data['name']
            )
            general_health.allergies.add(allergy)
        
        return general_health

    def update(self, instance, validated_data):
        chronic_diseases_data = validated_data.pop('chronic_diseases', None)
        medicines_data = validated_data.pop('medicines', None)
        allergies_data = validated_data.pop('allergies', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update chronic diseases if provided
        if chronic_diseases_data is not None:
            instance.chronic_diseases.clear()
            for chronic_disease_data in chronic_diseases_data:
                chronic_disease, _ = ChronicDisease.objects.get_or_create(
                    name=chronic_disease_data['name']
                )
                instance.chronic_diseases.add(chronic_disease)
        
        # Update medicines if provided
        if medicines_data is not None:
            instance.medicines.clear()
            for medicine_data in medicines_data:
                medicine, _ = Medicine.objects.get_or_create(
                    name=medicine_data['name']
                )
                instance.medicines.add(medicine)
        
        # Update allergies if provided
        if allergies_data is not None:
            instance.allergies.clear()
            for allergy_data in allergies_data:
                allergy, _ = Allergy.objects.get_or_create(
                    name=allergy_data['name']
                )
                instance.allergies.add(allergy)
        
        return instance
