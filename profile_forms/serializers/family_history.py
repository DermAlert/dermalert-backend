from rest_framework import serializers
from profile_forms.models import (
    FamilyHistory,
    Relatives,
    CancerTypes,
    InjuriesTreatment,
)
from .listed_items import (
    RelativesSerializer,
    CancerTypeSerializer,
    InjuriesTreatmentSerializer,
)


class FamilyHistorySerializer(serializers.ModelSerializer):
    family_history = RelativesSerializer(many=True, required=False)
    family_history_types = CancerTypeSerializer(many=True, required=False)
    patient_cancer_type = CancerTypeSerializer(many=True, required=False)
    injuries_treatment = InjuriesTreatmentSerializer(many=True, required=False)

    class Meta:
        model = FamilyHistory
        fields = [
            "id",
            "user",
            "family_history",
            "family_history_types",
            "patient_cancer_type",
            "injuries_treatment",
        ]
        read_only_fields = ("user",)

    def create(self, validated_data):
        relatives_data = validated_data.pop("family_history", [])
        family_types_data = validated_data.pop("family_history_types", [])
        patient_type_data = validated_data.pop("patient_cancer_type", [])
        treatments_data = validated_data.pop("injuries_treatment", [])

        instance = FamilyHistory.objects.create(**validated_data)

        for parent in relatives_data:
            parent_obj, _ = Relatives.objects.get_or_create(name=parent["name"])
            instance.family_history.add(parent_obj)

        for ct in family_types_data:
            ct_obj, _ = CancerTypes.objects.get_or_create(name=ct["name"])
            instance.family_history_types.add(ct_obj)

        for pt in patient_type_data:
            pt_obj, _ = CancerTypes.objects.get_or_create(name=pt["name"])
            instance.patient_cancer_type.add(pt_obj)

        for tr in treatments_data:
            tr_obj, _ = InjuriesTreatment.objects.get_or_create(name=tr["name"])
            instance.injuries_treatment.add(tr_obj)

        return instance

    def update(self, instance, validated_data):
        relatives_data = validated_data.pop("family_history", None)
        family_types_data = validated_data.pop("family_history_types", None)
        patient_type_data = validated_data.pop("patient_cancer_type", None)
        treatments_data = validated_data.pop("injuries_treatment", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if relatives_data is not None:
            instance.family_history.clear()
            for parent in relatives_data:
                parent_obj, _ = Relatives.objects.get_or_create(name=parent["name"])
                instance.family_history.add(parent_obj)

        if family_types_data is not None:
            instance.family_history_types.clear()
            for ct in family_types_data:
                ct_obj, _ = CancerTypes.objects.get_or_create(name=ct["name"])
                instance.family_history_types.add(ct_obj)

        if patient_type_data is not None:
            if patient_type_data:
                ct_obj, _ = CancerTypes.objects.get_or_create(
                    name=patient_type_data["name"]
                )
                instance.patient_cancer_type = ct_obj
            else:
                instance.patient_cancer_type = None

        if treatments_data is not None:
            instance.injuries_treatment.clear()
            for tr in treatments_data:
                tr_obj, _ = InjuriesTreatment.objects.get_or_create(name=tr["name"])
                instance.injuries_treatment.add(tr_obj)

        return instance
