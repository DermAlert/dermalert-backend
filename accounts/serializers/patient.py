from rest_framework import serializers
from accounts.models import Patient
from accounts.models import User
from accounts.enums.gender import Gender
from accounts.serializers.user import UserSerializer
from accounts.services import resolve_user_by_identity
from accounts.validators import validate_cpf
from health_unit.models import HealthUnit


class NestedUserSerializer(serializers.ModelSerializer):
    cpf = serializers.CharField(required=False, validators=[])
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ("id", "cpf", "email", "name", "password")
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def validate_cpf(self, value):
        try:
            return validate_cpf(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_email(self, value):
        email = (value or "").strip().lower()
        cpf = self.initial_data.get("cpf") if hasattr(self, "initial_data") else None
        existing_user = resolve_user_by_identity(cpf=cpf, email=email)
        if existing_user is not None:
            return email
        queryset = User.objects.exclude(email="")
        instance = getattr(self, "instance", None)
        if instance is not None:
            queryset = queryset.exclude(pk=instance.pk)
        if email and queryset.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email


class PatientSerializer(serializers.ModelSerializer):
    user = NestedUserSerializer()
    health_unit = serializers.PrimaryKeyRelatedField(
        queryset=HealthUnit.objects.filter(is_deleted=False),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Patient
        fields = [
            "sus_number",
            "phone_number",
            "gender",
            "other_gender",
            "date_of_birth",
            "health_unit",
            "user",
        ]

    def validate(self, attrs):
        gender = attrs.get("gender", getattr(self.instance, "gender", None))
        other_gender = attrs.get(
            "other_gender", getattr(self.instance, "other_gender", None)
        )

        if gender == Gender.OTHER and not other_gender:
            raise serializers.ValidationError(
                {"other_gender": "This field is required when gender is Other."}
            )

        if gender != Gender.OTHER:
            attrs["other_gender"] = None

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        cpf = user_data.get("cpf")
        email = user_data.get("email", "")
        password = user_data.pop("password", None)
        user = resolve_user_by_identity(cpf=cpf, email=email)

        if user is not None and hasattr(user, "patient_profile"):
            raise serializers.ValidationError("User already has a patient profile.")

        if user is None:
            if password:
                user_serializer = UserSerializer(data={**user_data, "password": password})
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
            else:
                user = User(
                    cpf=validate_cpf(cpf),
                    email=(email or "").strip().lower(),
                    name=user_data["name"],
                )
                user.set_unusable_password()
                user.save()
        else:
            if "cpf" in user_data:
                user.cpf = validate_cpf(user_data["cpf"])
            if "email" in user_data:
                user.email = (user_data["email"] or "").strip().lower()
            if "name" in user_data:
                user.name = user_data["name"]
            if password:
                user.set_password(password)
            user.save()

        patient = Patient.objects.create(user=user, **validated_data)
        return patient

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user_serializer = NestedUserSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            for field, value in user_serializer.validated_data.items():
                if field == "password":
                    instance.user.set_password(value)
                else:
                    setattr(instance.user, field, value)
            instance.user.save()

        for field in [
            "sus_number",
            "phone_number",
            "gender",
            "other_gender",
            "date_of_birth",
            "health_unit",
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
