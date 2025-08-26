from rest_framework import serializers
from profile_forms.models import ChronicDisease, Medicine, Allergy
from profile_forms.models import (
    ChronicDisease,
    Medicine,
    Allergy,
    Relatives,
    CancerTypes,
    InjuriesTreatment,
)


class ChronicDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicDisease
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class RelativesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatives
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class InjuriesTreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InjuriesTreatment
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}


class CancerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerTypes
        fields = ("id", "name")
        extra_kwargs = {"name": {"validators": []}}
