from datetime import date

import pytest
from django.urls import reverse
from django.test import override_settings
from pytest_factoryboy import register
from rest_framework.authtoken.models import Token

from accounts.enums.permission_role import PermissionRole
from accounts.models import Work
from .factories import HealthUnitFactory, PatientFactory, UserFactory

register(UserFactory)
register(PatientFactory)
register(HealthUnitFactory)


@pytest.mark.django_db
class TestRoleAccessAPI:
    def authenticate(self, api_client, user_factory, role=None, health_unit=None, is_staff=False):
        user = user_factory.create(is_staff=is_staff)
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        if role is not None:
            Work.objects.create(
                user=user,
                health_unit=health_unit or HealthUnitFactory.create(),
                permission_role=role,
                start_date=date(2026, 1, 1),
            )

        return user

    def test_manager_cannot_create_patient(
        self, api_client, user_factory, patient_factory, health_unit_factory
    ):
        health_unit = health_unit_factory.create()
        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.MANAGER,
            health_unit=health_unit,
        )
        new_patient = patient_factory.build()

        response = api_client.post(
            reverse("patient-list"),
            {
                "user": {
                    "cpf": new_patient.user.cpf,
                    "name": new_patient.user.name,
                    "email": new_patient.user.email,
                },
                "sus_number": new_patient.sus_number,
                "phone_number": new_patient.phone_number,
                "date_of_birth": new_patient.date_of_birth.isoformat(),
                "gender": new_patient.gender,
                "health_unit": health_unit.pk,
            },
            format="json",
        )

        assert response.status_code == 403

    def test_professional_can_create_cancer_research_and_manager_cannot(
        self, api_client, user_factory, patient_factory, health_unit_factory
    ):
        health_unit = health_unit_factory.create()
        patient = patient_factory.create(health_unit=health_unit)
        url = reverse("patient-cancer-research-list", kwargs={"user_pk": patient.pk})
        payload = {
            "suspicious_moles": True,
            "bleed_itch": False,
            "how_long": "1_3_months",
            "lesion_aspect": True,
            "diagnosis": "Suspicious lesion",
        }

        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.TECHNICIAN,
            health_unit=health_unit,
        )
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 201

        api_client.credentials()
        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.MANAGER,
            health_unit=health_unit,
        )
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 403

    def test_supervisor_can_list_professionals_alias_but_professional_cannot(
        self, api_client, user_factory, health_unit_factory
    ):
        health_unit = health_unit_factory.create()
        professional = user_factory.create()
        Work.objects.create(
            user=professional,
            health_unit=health_unit,
            permission_role=PermissionRole.TECHNICIAN,
            start_date=date(2026, 1, 1),
        )

        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.SUPERVISOR,
            health_unit=health_unit,
        )
        response = api_client.get(reverse("professional-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

        api_client.credentials()
        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.TECHNICIAN,
            health_unit=health_unit,
        )
        response = api_client.get(reverse("professional-list"))
        assert response.status_code == 403

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_supervisor_can_manage_professional_alias_crud(
        self, api_client, user_factory, health_unit_factory
    ):
        health_unit = health_unit_factory.create()
        professional_user = user_factory.create()
        assignment = Work.objects.create(
            user=professional_user,
            health_unit=health_unit,
            permission_role=PermissionRole.TECHNICIAN,
            start_date=date(2026, 1, 1),
        )

        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.SUPERVISOR,
            health_unit=health_unit,
        )

        list_response = api_client.get(reverse("professional-list"))
        assert list_response.status_code == 200
        assert list_response.data["count"] == 1

        create_response = api_client.post(
            reverse("professional-list"),
            {
                "name": "Nova Profissional",
                "cpf": "52998224725",
                "email": "nova.profissional@example.com",
                "health_unit": health_unit.pk,
            },
            format="json",
        )
        assert create_response.status_code == 201

        detail_url = reverse("professional-detail", kwargs={"pk": assignment.pk})

        retrieve_response = api_client.get(detail_url)
        assert retrieve_response.status_code == 200
        assert retrieve_response.data["id"] == assignment.pk

        put_response = api_client.put(
            detail_url,
            {
                "name": "Profissional Atualizada",
                "cpf": professional_user.cpf,
                "email": "profissional.atualizada@example.com",
                "permission_role": PermissionRole.TECHNICIAN,
                "start_date": "2026-01-15",
                "end_date": "2026-12-31",
            },
            format="json",
        )
        assert put_response.status_code == 200
        assert put_response.data["user"]["name"] == "Profissional Atualizada"
        assert put_response.data["user"]["email"] == "profissional.atualizada@example.com"
        assert put_response.data["start_date"] == "2026-01-15"

        patch_response = api_client.patch(
            detail_url,
            {
                "name": "Profissional Parcial",
            },
            format="json",
        )
        assert patch_response.status_code == 200
        assert patch_response.data["user"]["name"] == "Profissional Parcial"

        delete_response = api_client.delete(detail_url)
        assert delete_response.status_code == 204

    def test_manager_can_access_health_center_alias_but_professional_cannot(
        self, api_client, user_factory, health_unit_factory
    ):
        health_units = health_unit_factory.create_batch(2)

        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.MANAGER,
            health_unit=health_units[0],
        )
        response = api_client.get(reverse("health-center-list"))
        assert response.status_code == 200
        assert response.data["count"] == 2

        api_client.credentials()
        self.authenticate(
            api_client,
            user_factory,
            role=PermissionRole.TECHNICIAN,
            health_unit=health_units[0],
        )
        response = api_client.get(reverse("health-center-list"))
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "role",
        [PermissionRole.SUPERVISOR, PermissionRole.TECHNICIAN],
    )
    def test_supervisor_and_professional_can_view_own_health_center_detail(
        self, api_client, user_factory, health_unit_factory, role
    ):
        health_unit = health_unit_factory.create()

        self.authenticate(
            api_client,
            user_factory,
            role=role,
            health_unit=health_unit,
        )
        response = api_client.get(
            reverse("health-center-detail", kwargs={"pk": health_unit.pk})
        )

        assert response.status_code == 200
        assert response.data["id"] == health_unit.pk

    @pytest.mark.parametrize(
        "role",
        [PermissionRole.SUPERVISOR, PermissionRole.TECHNICIAN],
    )
    def test_supervisor_and_professional_can_view_own_health_center_patients(
        self, api_client, user_factory, patient_factory, health_unit_factory, role
    ):
        health_unit = health_unit_factory.create()
        patient_factory.create(health_unit=health_unit)

        self.authenticate(
            api_client,
            user_factory,
            role=role,
            health_unit=health_unit,
        )
        response = api_client.get(
            reverse("health-center-patients", kwargs={"pk": health_unit.pk})
        )

        assert response.status_code == 200
        assert response.data["count"] == 1

    @pytest.mark.parametrize(
        "role",
        [PermissionRole.SUPERVISOR, PermissionRole.TECHNICIAN],
    )
    def test_supervisor_and_professional_can_view_own_health_center_professionals(
        self, api_client, user_factory, health_unit_factory, role
    ):
        health_unit = health_unit_factory.create()
        professional = user_factory.create()
        Work.objects.create(
            user=professional,
            health_unit=health_unit,
            permission_role=PermissionRole.TECHNICIAN,
            start_date=date(2026, 1, 1),
        )

        self.authenticate(
            api_client,
            user_factory,
            role=role,
            health_unit=health_unit,
        )
        response = api_client.get(
            reverse("health-center-professionals", kwargs={"pk": health_unit.pk})
        )

        assert response.status_code == 200
        expected_count = 2 if role == PermissionRole.TECHNICIAN else 1
        assert response.data["count"] == expected_count

    @pytest.mark.parametrize(
        "role",
        [PermissionRole.SUPERVISOR, PermissionRole.TECHNICIAN],
    )
    def test_supervisor_and_professional_cannot_view_other_health_center(
        self, api_client, user_factory, health_unit_factory, role
    ):
        accessible_unit = health_unit_factory.create()
        other_unit = health_unit_factory.create()

        self.authenticate(
            api_client,
            user_factory,
            role=role,
            health_unit=accessible_unit,
        )
        response = api_client.get(
            reverse("health-center-detail", kwargs={"pk": other_unit.pk})
        )

        assert response.status_code == 403
