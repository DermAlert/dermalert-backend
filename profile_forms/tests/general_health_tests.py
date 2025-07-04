import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient
from .factories import GeneralHealthFactory, UserFactory, ChronicDiseaseFactory, MedicineFactory, AllergyFactory
from profile_forms.models import GeneralHealth
from profile_forms.enums.general_health import PhysicalActivityFrequency

register(GeneralHealthFactory)
register(UserFactory)
register(ChronicDiseaseFactory)
register(MedicineFactory)
register(AllergyFactory)

@pytest.mark.django_db(transaction=True)
class TestGeneralHealthAPI:
    def test_create(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        data = {
            "surgeries": "Appendectomy in 2020",
            "physical_activity_frequency": PhysicalActivityFrequency.DAILY,
            "chronic_diseases": [],
            "medicines": [],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 201
        assert resp.data["surgeries"] == data["surgeries"]
        assert resp.data["physical_activity_frequency"] == data["physical_activity_frequency"]
        assert resp.data["user"] == user.id

    def test_create_with_chronic_diseases(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        data = {
            "surgeries": "Heart surgery in 2019",
            "physical_activity_frequency": PhysicalActivityFrequency.THREE_TO_FIVE_TIMES_A_WEEK,
            "chronic_diseases": [
                {"name": "Diabetes"},
                {"name": "Hypertension"}
            ],
            "medicines": [],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 201
        assert len(resp.data["chronic_diseases"]) == 2

    def test_create_with_medicines(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        data = {
            "surgeries": "",
            "physical_activity_frequency": PhysicalActivityFrequency.NEVER,
            "chronic_diseases": [],
            "medicines": [
                {"name": "Aspirin"},
                {"name": "Metformin"}
            ],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 201
        assert len(resp.data["medicines"]) == 2

    def test_create_with_allergies(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        data = {
            "surgeries": "Knee replacement",
            "physical_activity_frequency": PhysicalActivityFrequency.OCCASIONALLY,
            "chronic_diseases": [],
            "medicines": [],
            "allergies": [
                {"name": "Peanuts"},
                {"name": "Shellfish"}
            ]
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 201
        assert len(resp.data["allergies"]) == 2

    def test_retrieve(self, api_client: APIClient, general_health_factory: GeneralHealthFactory):
        general_health = general_health_factory.create()
        url = reverse("patient-general-health-list", kwargs={"user_pk": general_health.user.id})
        
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["id"] == general_health.id
        assert resp.data["user"] == general_health.user.id
        assert resp.data["surgeries"] == general_health.surgeries
        assert resp.data["physical_activity_frequency"] == general_health.physical_activity_frequency

    def test_create_duplicate_for_same_user(self, api_client: APIClient, general_health_factory: GeneralHealthFactory):
        general_health = general_health_factory.create()
        url = reverse("patient-general-health-list", kwargs={"user_pk": general_health.user.id})
        
        data = {
            "surgeries": "Another surgery",
            "physical_activity_frequency": PhysicalActivityFrequency.DAILY,
            "chronic_diseases": [],
            "medicines": [],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 403
        assert "Já existe um formulário para esse CPF" in str(resp.data)

    def test_create_with_nonexistent_user(self, api_client: APIClient):
        url = reverse("patient-general-health-list", kwargs={"user_pk": 99999})
        
        data = {
            "surgeries": "Test surgery",
            "physical_activity_frequency": PhysicalActivityFrequency.DAILY,
            "chronic_diseases": [],
            "medicines": [],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 404

    def test_retrieve_nonexistent_general_health(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        resp = api_client.get(url)
        assert resp.status_code == 404

    def test_invalid_physical_activity_frequency(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})
        
        data = {
            "surgeries": "Test surgery",
            "physical_activity_frequency": "invalid_frequency",
            "chronic_diseases": [],
            "medicines": [],
            "allergies": []
        }
        
        resp = api_client.post(url, data=data, format='json')
        assert resp.status_code == 400
        assert "physical_activity_frequency" in resp.data
