from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.auth import (
    ChangeEmailSerializer,
    ChangeEmailResponseSerializer,
    ChangePasswordSerializer,
    ChangePasswordResponseSerializer,
    CompleteRegistrationSerializer,
    CompleteRegistrationResponseSerializer,
    CurrentUserSerializer,
    ForgotPasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    MessageSerializer,
    RegistrationInviteDetailSerializer,
    ResetPasswordSerializer,
)
from accounts.services import (
    complete_registration_invite,
    get_invite_from_token,
    send_password_reset_email,
)

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": CurrentUserSerializer(user).data,
            }
        )


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={204: "No content"})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: CurrentUserSerializer})
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={200: MessageSerializer},
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = (
            User.objects.filter(email__iexact=serializer.validated_data["email"])
            .exclude(email="")
            .first()
        )
        if user is not None:
            send_password_reset_email(user)

        return Response(
            {
                "message": "If the email exists, a password reset link has been sent."
            }
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={200: MessageSerializer},
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"detail": "Reset token is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(
            user, serializer.validated_data["token"]
        ):
            return Response(
                {"detail": "Reset token is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"message": "Password updated successfully."})


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: ChangePasswordResponseSerializer},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(
            serializer.validated_data["current_password"]
        ):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        Token.objects.filter(user=request.user).delete()
        new_token = Token.objects.create(user=request.user)
        return Response(
            {
                "message": "Password updated successfully.",
                "token": new_token.key,
            }
        )


class ChangeEmailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangeEmailSerializer,
        responses={200: ChangeEmailResponseSerializer},
    )
    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data["password"]):
            return Response(
                {"detail": "Password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["new_email"].strip().lower()
        if (
            User.objects.exclude(pk=request.user.pk)
            .exclude(email="")
            .filter(email__iexact=email)
            .exists()
        ):
            return Response(
                {"new_email": ["A user with that email already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.email = email
        request.user.save(update_fields=["email"])
        return Response({"message": "Email updated successfully.", "email": email})


class RegistrationInviteDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: RegistrationInviteDetailSerializer})
    def get(self, request, token):
        invite = get_invite_from_token(token)
        if invite is None or invite.is_deleted or not invite.is_active:
            return Response(
                {"detail": "Invite token is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invite.expires_at and invite.expires_at < timezone.now():
            return Response(
                {"detail": "Invite token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "name": invite.name,
                "cpf": invite.cpf,
                "email": invite.email,
                "health_unit": {
                    "id": invite.health_unit_code_id,
                    "name": invite.health_unit_code.name,
                },
                "permission_role": invite.permission_role,
            }
        )


class CompleteRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=CompleteRegistrationSerializer,
        responses={201: CompleteRegistrationResponseSerializer},
    )
    def post(self, request, token):
        serializer = CompleteRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite, user, work = complete_registration_invite(
            raw_token=token,
            password=serializer.validated_data["password"],
        )
        auth_token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "Registration completed successfully.",
                "token": auth_token.key,
                "user": CurrentUserSerializer(user).data,
                "assignment_id": work.pk,
                "invite_id": invite.pk,
            },
            status=status.HTTP_201_CREATED,
        )
