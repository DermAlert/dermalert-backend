import pytest
from django.urls import reverse
from pytest_factoryboy import register
from .factories import PatientFactory, UserFactory

@pytest.mark.django_db
class TestPatientAPI:
    register(PatientFactory)
    register(UserFactory)

    def test_list(self, api_client, patient_factory):
        patient_factory.create_batch(3)
        url = reverse("patient-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 3

    def test_create(self, api_client, patient_factory):
        new_patient = patient_factory.build()
        url = reverse("patient-list")
        resp = api_client.post(url, data={
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
        }, format='json')

        assert resp.status_code == 201
        assert resp.data["sus_number"] == new_patient.sus_number
        assert resp.data["phone_number"] == new_patient.phone_number
        assert resp.data["user"]["cpf"] == new_patient.user.cpf
        assert resp.data["user"]["email"] == new_patient.user.email
    
    def test_create_with_other_gender(self, api_client, patient_factory):
        new_patient = patient_factory.build()
        url = reverse("patient-list")
        resp = api_client.post(url, data={
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
        }, format='json')
        assert resp.status_code == 201
        assert resp.data["other_gender"] == "Non-binary"
        assert resp.data["sus_number"] == new_patient.sus_number
        assert resp.data["phone_number"] == new_patient.phone_number
        assert resp.data["user"]["cpf"] == new_patient.user.cpf
        assert resp.data["user"]["email"] == new_patient.user.email

    def test_retrieve(self, api_client, patient_factory):
        patient = patient_factory.create()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["sus_number"] == patient.sus_number
        assert resp.data["phone_number"] == patient.phone_number
        assert resp.data["user"]["cpf"] == patient.user.cpf
        assert resp.data["user"]["email"] == patient.user.email

    def test_update(self, api_client, patient_factory):
        patient = patient_factory.create()
        url = reverse("patient-detail", kwargs={"pk": patient.pk})
        updated_data = {
            "phone_number": "9876543210",
            "user": {
                "email": "new-email@email.com",
            },
        }
        resp = api_client.patch(url, data=updated_data, format='json')
        assert resp.status_code == 200
        assert resp.data["phone_number"] == updated_data["phone_number"]
        assert resp.data["user"]["email"] == updated_data["user"]["email"]

    def test_create_with_existing_user(self, api_client, user_factory):
        existing_user = user_factory.create()
        url = reverse("patient-list")
        resp = api_client.post(url, data={
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
        }, format='json')
        assert resp.status_code == 201
        assert resp.data["user"]["id"] == existing_user.id
        assert resp.data["sus_number"] == "12345678901"


