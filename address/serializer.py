# addresses/serializers.py
from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "cep",
            "country",
            "state",
            "city",
            "neighborhood",
            "street",
            "number",
            "longitude",
            "latitude",
        )

    def create(self, validated_data):
        cep = validated_data.get("cep")
        number = validated_data.get("number")

        address, created = Address.objects.get_or_create(
            cep=cep,
            number=number,
            defaults={
                "country": validated_data.get("country"),
                "state": validated_data.get("state"),
                "city": validated_data.get("city"),
                "neighborhood": validated_data.get("neighborhood"),
                "street": validated_data.get("street"),
                "longitude": validated_data.get("longitude"),
                "latitude": validated_data.get("latitude"),
            },
        )
        return address


class CepRequestSerializer(serializers.Serializer):
    cep = serializers.RegexField(regex=r"^\d{8}$")


class AddressResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "cep",
            "country",
            "state",
            "city",
            "neighborhood",
            "street",
        )

    def is_valid(self, *, raise_exception=False):
        """
        Override is_valid to ensure that the response data is valid.
        """
        if "cep" in self.initial_data:
            self.initial_data["cep"] = self.initial_data["cep"].replace("-", "")
        super().is_valid(raise_exception=raise_exception)
        return self.validated_data
