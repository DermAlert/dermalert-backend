from django.contrib.auth import authenticate
from rest_framework import serializers

from accounts.models import Work


class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            cpf=attrs["cpf"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError({"detail": "CPF or password is invalid."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User is inactive."})

        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class ChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_email = serializers.EmailField()


class CompleteRegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    cpf = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    permission_roles = serializers.SerializerMethodField()
    health_unit_ids = serializers.SerializerMethodField()

    def get_permission_roles(self, obj):
        return list(
            Work.objects.filter(
                user=obj,
                is_active=True,
                is_deleted=False,
            ).values_list("permission_role", flat=True)
        )

    def get_health_unit_ids(self, obj):
        return list(
            Work.objects.filter(
                user=obj,
                is_active=True,
                is_deleted=False,
            ).values_list("health_unit_id", flat=True)
        )


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    user = CurrentUserSerializer(read_only=True)


class ChangePasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)


class ChangeEmailResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class RegistrationInviteHealthUnitSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class RegistrationInviteDetailSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    cpf = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    health_unit = RegistrationInviteHealthUnitSerializer(read_only=True)
    permission_role = serializers.CharField(read_only=True)


class CompleteRegistrationResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    user = CurrentUserSerializer(read_only=True)
    assignment_id = serializers.IntegerField(read_only=True)
    invite_id = serializers.IntegerField(read_only=True)
