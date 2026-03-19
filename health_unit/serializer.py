from rest_framework import serializers

from accounts.models import Patient, Work
from address.models import Address
from address.serializer import AddressSerializer
from health_unit.models import HealthUnit


class HealthUnitSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.filter(is_deleted=False),
        source="address",
        write_only=True,
    )
    patient_count = serializers.SerializerMethodField()
    professional_count = serializers.SerializerMethodField()

    class Meta:
        model = HealthUnit
        fields = [
            "id",
            "name",
            "email",
            "address",
            "address_id",
            "patient_count",
            "professional_count",
        ]

    def get_patient_count(self, obj):
        return Patient.objects.filter(
            health_unit=obj,
            is_deleted=False,
            is_active=True,
        ).count()

    def get_professional_count(self, obj):
        return Work.objects.filter(
            health_unit=obj,
            is_deleted=False,
            is_active=True,
        ).count()
