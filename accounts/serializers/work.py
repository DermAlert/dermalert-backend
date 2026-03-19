from django.utils import timezone
from rest_framework import serializers

from accounts.enums.permission_role import PermissionRole
from accounts.models import Work
from accounts.validators import validate_cpf
from health_unit.models import HealthUnit


class ProfessionalUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    cpf = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class ProfessionalHealthUnitSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class ProfessionalAssignmentSerializer(serializers.ModelSerializer):
    user = ProfessionalUserSerializer(read_only=True)
    health_unit = ProfessionalHealthUnitSerializer(read_only=True)
    registration_pending = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "permission_role",
            "start_date",
            "end_date",
            "is_active",
            "registration_pending",
            "user",
            "health_unit",
        ]

    def get_registration_pending(self, obj):
        return not (obj.user.is_active and obj.user.has_usable_password())


class ProfessionalAssignmentWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    cpf = serializers.CharField(max_length=14)
    email = serializers.EmailField()
    health_unit = serializers.PrimaryKeyRelatedField(
        queryset=HealthUnit.objects.filter(is_deleted=False)
    )
    permission_role = serializers.ChoiceField(
        choices=PermissionRole.choices,
        required=False,
        default=PermissionRole.TECHNICIAN,
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate_cpf(self, value):
        try:
            return validate_cpf(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_email(self, value):
        return (value or "").strip().lower()

    def validate(self, attrs):
        start_date = attrs.get("start_date") or timezone.localdate()
        end_date = attrs.get("end_date")

        if end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        attrs["start_date"] = start_date
        return attrs


class ProfessionalAssignmentUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    cpf = serializers.CharField(max_length=14, required=False)
    email = serializers.EmailField(required=False)
    permission_role = serializers.ChoiceField(
        choices=PermissionRole.choices,
        required=False,
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate_cpf(self, value):
        try:
            return validate_cpf(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_email(self, value):
        return (value or "").strip().lower()

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs
