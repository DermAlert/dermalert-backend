from rest_framework import serializers
from accounts.models import Patient
from accounts.models import User
from accounts.serializers.user import UserSerializer


class NestedUserSerializer(serializers.ModelSerializer):
    cpf = serializers.CharField(required=True, validators=[])

    class Meta:
        model = User
        fields = ("id", "cpf", "email", "name")
        extra_kwargs = {
            "cpf": {"required": True},
        }


class PatientSerializer(serializers.ModelSerializer):
    user = NestedUserSerializer()
    
    class Meta:
        model = Patient
        fields = [
            "sus_number",
            "phone_number",
            "gender",
            "other_gender",
            "date_of_birth",
            "user",
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        cpf = user_data.get("cpf")
        user = None
        try:
            user = User.objects.get(cpf=cpf)
        except:
            pass
        if not user:
            user_data["password"] = "12345678"  # Default password, should be changed later
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
        else:
            try:
                _ = user.patient_profile
            except:
                pass
            else:
                raise serializers.ValidationError("User already has a patient profile.")

        patient = Patient.objects.create(user=user, **validated_data)
        return patient

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user_serializer = UserSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance
