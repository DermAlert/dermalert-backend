import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_factoryboy import register
from rest_framework.authtoken.models import Token

from .factories import UserFactory

register(UserFactory)

User = get_user_model()


@pytest.mark.django_db
class TestAuthAPI:
    def test_login_returns_token(self, api_client, user_factory):
        user = user_factory.create()
        user.set_password("s3nh4-forte")
        user.save()

        response = api_client.post(
            reverse("auth-login"),
            {"cpf": user.cpf, "password": "s3nh4-forte"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["token"]
        assert response.data["user"]["cpf"] == user.cpf

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_forgot_password_sends_email(self, api_client, user_factory):
        user = user_factory.create(email="reset@example.com")

        response = api_client.post(
            reverse("auth-forgot-password"),
            {"email": user.email},
            format="json",
        )

        assert response.status_code == 200
        assert len(mail.outbox) == 1
        assert "reset-password" in mail.outbox[0].body

    def test_reset_password_updates_credentials(self, api_client, user_factory):
        user = user_factory.create()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = api_client.post(
            reverse("auth-reset-password"),
            {
                "uid": uid,
                "token": token,
                "new_password": "nova-senha-segura",
            },
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("nova-senha-segura")

    def test_change_password_requires_authentication(self, api_client, user_factory):
        user = user_factory.create()
        user.set_password("senha-antiga")
        user.save()
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = api_client.post(
            reverse("auth-change-password"),
            {
                "current_password": "senha-antiga",
                "new_password": "senha-nova",
            },
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("senha-nova")
        assert response.data["token"]

    def test_change_email_requires_correct_password(self, api_client, user_factory):
        user = user_factory.create(email="old@example.com")
        user.set_password("senha-antiga")
        user.save()
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = api_client.post(
            reverse("auth-change-email"),
            {
                "password": "senha-antiga",
                "new_email": "new@example.com",
            },
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == "new@example.com"
