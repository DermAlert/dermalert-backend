from rest_framework import serializers
from django.contrib.auth import get_user_model
from address.serializer import AddressSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "cpf",
            "email",
            "first_name",
            "last_name",
            "password",
            "address",
        )
        read_only_fields = ("id", "is_staff", "is_admin")
        extra_kwargs = {
            "cpf": {"required": True},
        }

    def validate_cpf(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("CPF must be a 11-digit number.")
        return value

    def create(self, validated_data):
        user, create = User.objects.get_or_create(
            cpf=validated_data["cpf"],
            defaults={
                "email": validated_data["email"],
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
                "password": validated_data["password"],
            },
        )

        # if user already exists, update the fields
        if not create:
            user.email = validated_data["email"]
            user.first_name = validated_data["first_name"]
            user.last_name = validated_data["last_name"]
            user.set_password(validated_data["password"])
            user.save()

        return user
