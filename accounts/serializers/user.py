from rest_framework import serializers
from django.contrib.auth import get_user_model
from address.serializer import AddressSerializer
from accounts.validators import validate_cpf

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "cpf",
            "email",
            "name",
            "password",
            "address",
            "is_active",
        )
        read_only_fields = ("id", "address", "is_active")
        extra_kwargs = {
            "cpf": {"required": True},
        }

    def validate_cpf(self, value):
        try:
            return validate_cpf(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_email(self, value):
        email = (value or "").strip().lower()
        queryset = User.objects.exclude(email="")
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if email and queryset.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")

        return email

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "This field is required."})
        return attrs

    def create(self, validated_data):
        if User.objects.filter(cpf=validated_data["cpf"]).exists():
            raise serializers.ValidationError({"cpf": "A user with that cpf already exists."})

        return User.objects.create_user(
            cpf=validated_data["cpf"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            name=validated_data["name"],
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
