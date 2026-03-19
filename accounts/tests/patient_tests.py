from datetime import date

import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.authtoken.models import Token
from accounts.enums.permission_role import PermissionRole
from accounts.models import Work
from .factories import HealthUnitFactory, PatientFactory, UserFactory


@pytest.mark.django_db
class TestPatientAPI:
    register(PatientFactory)
    register(UserFactory)
    register(HealthUnitFactory)

    def authenticate_professional(self, api_client, user_factory, health_unit_factory):
        health_unit = health_unit_factory.create()
        professional = user_factory.create()
        token = Token.objects.create(user=professional)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        Work.objects.create(
            user=professional,
            health_unit=health_unit,
            permission_role=PermissionRole.TECHNICIAN,
            start_date=date(2026, 1, 1),
        )
        return health_unit

    def test_list(self, api_client, patient_factory, user_factory, health_unit_factory):
        health_unit = self.authenticate_professional(
            api_client, user_factory, health_unit_factory
        )
        patients = patient_factory.create_batch(3)
        for patient in patients:
            patient.health_unit = health_unit
            patient.save()
        url = reverse("patient-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 3

    def test_create(self, api_client, patient_factory, user_factory, health_unit_factory):
        self.authenticate_professional(api_client, user_factory, health_unit_factory)
        new_patient = patient_factory.build()
        url = reverse("patient-list")
        resp = api_client.post(
            url,
            data={
                "user": {
                    "cpf": new_patient.user.cpf,
                    "name": new_patient.user.name,
                    "email": new_patient.user.email,
                    "password": new_patient.user.password,
                },
                "sus_number": new_patient.sus_number,
                "phone_number": new_patient.phone_number,
                "date_of_birth": new_patient.date_of_birth.isoformat(),
                "gender": new_patient.gender,
            },
            format="json",
        )

        assert resp.status_code == 201
        assert resp.data["sus_number"] == new_patient.sus_number
        assert resp.data["phone_number"] == new_patient.phone_number
        assert resp.data["user"]["cpf"] == new_patient.user.cpf
        assert resp.data["user"]["email"] == new_patient.user.email

    def test_create_with_other_gender(
        self, api_client, patient_factory, user_factory, health_unit_factory
    ):
        self.authenticate_professional(api_client, user_factory, health_unit_factory)
        new_patient = patient_factory.build()
        url = reverse("patient-list")
        resp = api_client.post(
            url,
            data={
                "user": {
                    "cpf": new_patient.user.cpf,
                    "name": new_patient.user.name,
                    "email": new_patient.user.email,
                    "password": new_patient.user.password,
                },
                "sus_number": new_patient.sus_number,
                "phone_number": new_patient.phone_number,
                "date_of_birth": new_patient.date_of_birth.isoformat(),
                "gender": "O",
                "other_gender": "Non-binary",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["other_gender"] == "Non-binary"
        assert resp.data["sus_number"] == new_patient.sus_number
        assert resp.data["phone_number"] == new_patient.phone_number
        assert resp.data["user"]["cpf"] == new_patient.user.cpf
        assert resp.data["user"]["email"] == new_patient.user.email

    def test_retrieve(self, api_client, patient_factory, user_factory, health_unit_factory):
        health_unit = self.authenticate_professional(
            api_client, user_factory, health_unit_factory
        )
        patient = patient_factory.create()
        patient.health_unit = health_unit
        patient.save()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["sus_number"] == patient.sus_number
        assert resp.data["phone_number"] == patient.phone_number
        assert resp.data["user"]["cpf"] == patient.user.cpf
        assert resp.data["user"]["email"] == patient.user.email

    def test_update(self, api_client, patient_factory, user_factory, health_unit_factory):
        health_unit = self.authenticate_professional(
            api_client, user_factory, health_unit_factory
        )
        patient = patient_factory.create()
        patient.health_unit = health_unit
        patient.save()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        updated_data = {
            "phone_number": "9876543210",
            "user": {
                "email": "new-email@email.com",
            },
        }
        resp = api_client.patch(url, data=updated_data, format="json")
        assert resp.status_code == 200
        assert resp.data["phone_number"] == updated_data["phone_number"]
        assert resp.data["user"]["email"] == updated_data["user"]["email"]

    def test_update_gender_sus_and_health_unit(
        self, api_client, patient_factory, health_unit_factory, user_factory
    ):
        current_unit = self.authenticate_professional(
            api_client, user_factory, health_unit_factory
        )
        patient = patient_factory.create()
        patient.health_unit = current_unit
        patient.save()
        health_unit = health_unit_factory.create()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})

        resp = api_client.patch(
            url,
            data={
                "sus_number": "123456789012345",
                "gender": "O",
                "other_gender": "Nao-binario",
                "health_unit": health_unit.pk,
            },
            format="json",
        )

        assert resp.status_code == 403

    def test_create_with_existing_user(
        self, api_client, user_factory, health_unit_factory
    ):
        self.authenticate_professional(api_client, user_factory, health_unit_factory)
        existing_user = user_factory.create()
        url = reverse("patient-list")
        resp = api_client.post(
            url,
            data={
                "user": {
                    "id": existing_user.id,
                    "cpf": existing_user.cpf,
                    "name": existing_user.name,
                    "email": existing_user.email,
                    "password": existing_user.password,
                },
                "sus_number": "12345678901",
                "phone_number": "1234567890",
                "date_of_birth": "2000-01-01",
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["user"]["id"] == existing_user.id
        assert resp.data["sus_number"] == "12345678901"

    def test_delete_soft_deletes_patient(
        self, api_client, patient_factory, user_factory, health_unit_factory
    ):
        health_unit = self.authenticate_professional(
            api_client, user_factory, health_unit_factory
        )
        patient = patient_factory.create()
        patient.health_unit = health_unit
        patient.save()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})

        resp = api_client.delete(url)

        assert resp.status_code == 204
        patient.refresh_from_db()
        assert patient.is_deleted is True
        assert patient.is_active is False
