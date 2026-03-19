import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.authtoken.models import Token

from accounts.enums.permission_role import PermissionRole
from accounts.models import InviteWork, Work
from .factories import HealthUnitFactory, UserFactory, WorkFactory

register(UserFactory)
register(HealthUnitFactory)
register(WorkFactory)

User = get_user_model()


def extract_token_from_email(body: str) -> str:
    match = re.search(r"token=([^&\s]+)", body)
    assert match is not None
    return match.group(1)


@pytest.mark.django_db
class TestProfessionalAssignmentsAPI:
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_invites_new_professional(self, api_client, user_factory, health_unit_factory):
        admin = user_factory.create(is_staff=True)
        token = Token.objects.create(user=admin)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        health_unit = health_unit_factory.create()

        response = api_client.post(
            reverse("professional-assignment-list"),
            {
                "name": "Maria Tecnica",
                "cpf": "52998224725",
                "email": "maria@example.com",
                "health_unit": health_unit.pk,
                "permission_role": PermissionRole.TECHNICIAN,
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["status"] == "invited"
        assignment = Work.objects.get(pk=response.data["assignment"]["id"])
        assert assignment.is_active is False
        assert InviteWork.objects.filter(user=assignment.user).exists()
        assert len(mail.outbox) == 1

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_links_existing_professional(self, api_client, user_factory, health_unit_factory):
        admin = user_factory.create(is_staff=True)
        token = Token.objects.create(user=admin)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        health_unit = health_unit_factory.create()

        professional = user_factory.create(
            cpf="52998224725",
            email="existing@example.com",
            name="Existing Professional",
        )
        professional.set_password("senha-forte")
        professional.save()

        response = api_client.post(
            reverse("professional-assignment-list"),
            {
                "name": professional.name,
                "cpf": professional.cpf,
                "email": professional.email,
                "health_unit": health_unit.pk,
                "permission_role": PermissionRole.TECHNICIAN,
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["status"] == "linked"
        assignment = Work.objects.get(pk=response.data["assignment"]["id"])
        assert assignment.is_active is True
        assert len(mail.outbox) == 1

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_complete_registration_from_invite(self, api_client, user_factory, health_unit_factory):
        admin = user_factory.create(is_staff=True)
        token = Token.objects.create(user=admin)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        health_unit = health_unit_factory.create()

        create_response = api_client.post(
            reverse("professional-assignment-list"),
            {
                "name": "Novo Profissional",
                "cpf": "52998224725",
                "email": "novo@example.com",
                "health_unit": health_unit.pk,
                "permission_role": PermissionRole.TECHNICIAN,
            },
            format="json",
        )

        assert create_response.status_code == 201
        raw_token = extract_token_from_email(mail.outbox[0].body)

        detail_response = api_client.get(
            reverse("auth-invitation-detail", kwargs={"token": raw_token})
        )
        assert detail_response.status_code == 200
        assert detail_response.data["email"] == "novo@example.com"

        complete_response = api_client.post(
            reverse("auth-invitation-complete", kwargs={"token": raw_token}),
            {"password": "senha-super-segura"},
            format="json",
        )

        assert complete_response.status_code == 201
        user = User.objects.get(email="novo@example.com")
        assert user.is_active is True
        assert user.check_password("senha-super-segura")
        assignment = Work.objects.get(user=user, health_unit=health_unit)
        assert assignment.is_active is True

    def test_supervisor_cannot_be_linked_to_two_units(
        self, api_client, user_factory, health_unit_factory, work_factory
    ):
        admin = user_factory.create(is_staff=True)
        token = Token.objects.create(user=admin)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        supervisor = user_factory.create(
            cpf="52998224725",
            email="supervisor@example.com",
            name="Supervisor",
        )
        supervisor.set_password("senha-forte")
        supervisor.save()

        first_unit = health_unit_factory.create()
        second_unit = health_unit_factory.create()
        work_factory.create(
            user=supervisor,
            health_unit=first_unit,
            permission_role=PermissionRole.SUPERVISOR,
        )

        response = api_client.post(
            reverse("professional-assignment-list"),
            {
                "name": supervisor.name,
                "cpf": supervisor.cpf,
                "email": supervisor.email,
                "health_unit": second_unit.pk,
                "permission_role": PermissionRole.SUPERVISOR,
            },
            format="json",
        )

        assert response.status_code == 400
        assert Work.objects.filter(
            user=supervisor,
            permission_role=PermissionRole.SUPERVISOR,
            is_deleted=False,
        ).count() == 1
