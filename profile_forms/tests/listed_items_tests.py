import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient
from .factories import (
    ChronicDiseaseFactory,
    MedicineFactory,
    AllergyFactory,
    UserFactory,
)
from profile_forms.models import ChronicDisease, Medicine, Allergy

register(ChronicDiseaseFactory)
register(MedicineFactory)
register(AllergyFactory)
register(UserFactory)


@pytest.mark.django_db(transaction=True)
class TestChronicDiseaseAPI:
    @pytest.fixture(autouse=True)
    def setup_clean_db(self):
        """Clean database before each test"""
        ChronicDisease.objects.all().delete()
        Medicine.objects.all().delete()
        Allergy.objects.all().delete()

    def test_list(
        self, api_client: APIClient, chronic_disease_factory: ChronicDiseaseFactory
    ):
        chronic_disease_factory.create_batch(3)
        url = reverse("chronic-disease-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 3

    def test_search_by_name(
        self, api_client: APIClient, chronic_disease_factory: ChronicDiseaseFactory
    ):
        diabetes = chronic_disease_factory.create(name="TestDiabetes")
        hypertension = chronic_disease_factory.create(name="TestHypertension")
        chronic_disease_factory.create(name="TestOtherDisease")

        url = f"{reverse('chronic-disease-list')}?search=TestDiabetes"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["name"] == diabetes.name

    def test_search_partial_match(
        self, api_client: APIClient, chronic_disease_factory: ChronicDiseaseFactory
    ):
        chronic_disease_factory.create(name="TestType1Diabetes")
        chronic_disease_factory.create(name="TestType2Diabetes")
        chronic_disease_factory.create(name="TestHypertension")

        url = f"{reverse('chronic-disease-list')}?search=TestType"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_empty_search(
        self, api_client: APIClient, chronic_disease_factory: ChronicDiseaseFactory
    ):
        chronic_disease_factory.create_batch(5)
        url = f"{reverse('chronic-disease-list')}?search="
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 5


@pytest.mark.django_db(transaction=True)
class TestMedicineAPI:
    @pytest.fixture(autouse=True)
    def setup_clean_db(self):
        """Clean database before each test"""
        ChronicDisease.objects.all().delete()
        Medicine.objects.all().delete()
        Allergy.objects.all().delete()

    def test_list(self, api_client: APIClient, medicine_factory: MedicineFactory):
        medicine_factory.create_batch(4)
        url = reverse("medicine-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 4

    def test_search_by_name(
        self, api_client: APIClient, medicine_factory: MedicineFactory
    ):
        aspirin = medicine_factory.create(name="TestAspirin")
        ibuprofen = medicine_factory.create(name="TestIbuprofen")
        medicine_factory.create(name="TestParacetamol")

        url = f"{reverse('medicine-list')}?search=TestAspirin"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["name"] == aspirin.name

    def test_search_case_insensitive(
        self, api_client: APIClient, medicine_factory: MedicineFactory
    ):
        medicine_factory.create(name="TestMetformin")
        medicine_factory.create(name="TestInsulin")

        url = f"{reverse('medicine-list')}?search=testmetformin"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_no_results_search(
        self, api_client: APIClient, medicine_factory: MedicineFactory
    ):
        medicine_factory.create_batch(3)
        url = f"{reverse('medicine-list')}?search=nonexistent"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 0


@pytest.mark.django_db(transaction=True)
class TestAllergyAPI:
    @pytest.fixture(autouse=True)
    def setup_clean_db(self):
        """Clean database before each test"""
        ChronicDisease.objects.all().delete()
        Medicine.objects.all().delete()
        Allergy.objects.all().delete()

    def test_list(self, api_client: APIClient, allergy_factory: AllergyFactory):
        allergy_factory.create_batch(2)
        url = reverse("allergy-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_search_by_name(
        self, api_client: APIClient, allergy_factory: AllergyFactory
    ):
        peanuts = allergy_factory.create(name="TestPeanuts")
        shellfish = allergy_factory.create(name="TestShellfish")
        allergy_factory.create(name="TestLactose")

        url = f"{reverse('allergy-list')}?search=TestPeanuts"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["name"] == peanuts.name

    def test_search_multiple_results(
        self, api_client: APIClient, allergy_factory: AllergyFactory
    ):
        allergy_factory.create(name="TestTreeNuts")
        allergy_factory.create(name="TestGroundNuts")
        allergy_factory.create(name="TestDairy")

        url = f"{reverse('allergy-list')}?search=Nuts"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_ordered_results(
        self, api_client: APIClient, allergy_factory: AllergyFactory
    ):
        # Create allergies in random order
        allergy_factory.create(name="TestZebraAllergy")
        allergy_factory.create(name="TestAppleAllergy")
        allergy_factory.create(name="TestMilkAllergy")

        url = reverse("allergy-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        # Should be ordered alphabetically by name
        names = [item["name"] for item in resp.data]
        assert names == sorted(names)


@pytest.mark.django_db(transaction=True)
class TestListedItemsIntegration:
    @pytest.fixture(autouse=True)
    def setup_clean_db(self):
        """Clean database before each test"""
        ChronicDisease.objects.all().delete()
        Medicine.objects.all().delete()
        Allergy.objects.all().delete()

    def test_create_general_health_with_existing_items(
        self,
        api_client: APIClient,
        user_factory,
    ):
        """Test creating GeneralHealth with chronic diseases, medicines, and allergies"""
        user = user_factory.create()

        url = reverse("patient-general-health-list", kwargs={"user_pk": user.id})

        data = {
            "surgeries": "Test surgery",
            "physical_activity_frequency": "daily",
            "chronic_diseases": [{"name": "TestDiabetes"}],
            "medicines": [{"name": "TestAspirin"}],
            "allergies": [{"name": "TestPeanuts"}],
        }

        resp = api_client.post(url, data=data, format="json")
        assert resp.status_code == 201
        assert len(resp.data["chronic_diseases"]) == 1
        assert len(resp.data["medicines"]) == 1
        assert len(resp.data["allergies"]) == 1
        assert resp.data["chronic_diseases"][0]["name"] == "TestDiabetes"
        assert resp.data["medicines"][0]["name"] == "TestAspirin"
        assert resp.data["allergies"][0]["name"] == "TestPeanuts"
