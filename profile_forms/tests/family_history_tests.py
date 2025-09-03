import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import (
    UserFactory,
    RelativesFactory,
    CancerTypesFactory,
    InjuriesTreatmentFactory,
)
from profile_forms.models import (
    Relatives,
    CancerTypes,
    InjuriesTreatment,
)

register(UserFactory)
register(RelativesFactory)
register(CancerTypesFactory)
register(InjuriesTreatmentFactory)


@pytest.mark.django_db(transaction=True)
class TestFamilyHistoryAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
        data = {
            "family_history": [{"name": "Mãe"}, {"name": "Pai"}],
            "family_history_types": [{"name": "Melanoma"}],
            "patient_cancer_type": [{"name": "Melanoma"}],
            "injuries_treatment": [{"name": "Cirurgia excisional"}],
        }
        resp = api_client.post(url, data=data, format="json")
        assert resp.status_code == 201
        assert resp.data["user"] == user.id
        assert len(resp.data["family_history"]) == 2
        assert len(resp.data["family_history_types"]) == 1
        assert resp.data["patient_cancer_type"][0]["name"] == "Melanoma"
        assert len(resp.data["injuries_treatment"]) == 1

    def test_create_without_optional_lists(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
        data = {}
        resp = api_client.post(url, data=data, format="json")
        assert resp.status_code == 201
        assert resp.data["family_history"] == []
        assert resp.data["family_history_types"] == []
        assert resp.data["patient_cancer_type"] == []
        assert resp.data["injuries_treatment"] == []

    def test_create_duplicate_for_same_user(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
        data = {}
        first = api_client.post(url, data=data, format="json")
        assert first.status_code == 201
        second = api_client.post(url, data=data, format="json")
        assert second.status_code == 403
        assert "Já existe um formulário" in str(second.data)

    def test_retrieve(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
        create = api_client.post(url, data={}, format="json")
        assert create.status_code == 201
        get_resp = api_client.get(url)
        assert get_resp.status_code == 200
        assert get_resp.data["id"] == create.data["id"]

    """
    TODO: Criar rotas para permitir update
    """
    # def test_update_lists(self, api_client: APIClient, user_factory: UserFactory):
    #     user = user_factory.create()
    #     url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
    #     create = api_client.post(url, data={}, format="json")
    #     assert create.status_code == 201
    #     # PUT should replace lists
    #     update_data = {
    #         "family_history": [ {"name": "Irmã"} ],
    #         "family_history_types": [ {"name": "Carinoma Basocelular"} ],
    #         "patient_cancer_type": {"name": "Carinoma Espinocelular"},
    #         "injuries_treatment": [ {"name": "Crioterapia"}, {"name": "Laser"} ],
    #     }
    #     put_resp = api_client.put(url, data=update_data, format="json")
    #     assert put_resp.status_code == 200
    #     assert len(put_resp.data["family_history"]) == 1
    #     assert put_resp.data["family_history"][0]["name"] == "Irmã"
    #     assert len(put_resp.data["injuries_treatment"]) == 2
    #     assert put_resp.data["patient_cancer_type"]["name"] == "Carinoma Espinocelular"

    # def test_update_clear_patient_cancer_type(self, api_client: APIClient, user_factory: UserFactory):
    #     user = user_factory.create()
    #     url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
    #     create = api_client.post(url, data={
    #         "patient_cancer_type": {"name": "Melanoma"}
    # #     }, format="json")
    #     assert create.status_code == 201
    #     put_resp = api_client.put(url, data={"patient_cancer_type": None}, format="json")
    #     assert put_resp.status_code == 200
    #     assert put_resp.data["patient_cancer_type"] is None

    def test_nonexistent_user(self, api_client: APIClient):
        url = reverse("patient-family-history-list", kwargs={"user_pk": 999999})
        resp = api_client.post(url, data={}, format="json")
        assert resp.status_code == 404

    def test_retrieve_nonexistent_form(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-family-history-list", kwargs={"user_pk": user.id})
        resp = api_client.get(url)
        assert resp.status_code == 404


@pytest.mark.django_db(transaction=True)
class TestFamilyHistoryListedItems:
    @pytest.fixture(autouse=True)
    def clean(self):
        Relatives.objects.all().delete()
        CancerTypes.objects.all().delete()
        InjuriesTreatment.objects.all().delete()

    def test_relatives_list_and_search(
        self, api_client: APIClient, relatives_factory: RelativesFactory
    ):
        relatives_factory.create(name="Mãe")
        relatives_factory.create(name="Pai")
        relatives_factory.create(name="Irmão")
        url = reverse("relatives-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert len(resp.data) == 3
        search_resp = api_client.get(f"{url}?search=Pai")
        assert search_resp.status_code == 200
        assert len(search_resp.data) == 1
        assert search_resp.data[0]["name"] == "Pai"

    def test_cancer_types_search_partial(
        self, api_client: APIClient, cancer_types_factory: CancerTypesFactory
    ):
        cancer_types_factory.create(name="Melanoma")
        cancer_types_factory.create(name="Carinoma Basocelular")
        cancer_types_factory.create(name="Carinoma Espinocelular")
        url = reverse("cancer-type-list")
        resp = api_client.get(f"{url}?search=Carinoma")
        assert resp.status_code == 200
        # Should return the two Carinoma items
        names = sorted([r["name"] for r in resp.data])
        assert names == ["Carinoma Basocelular", "Carinoma Espinocelular"]

    def test_injuries_treatments_ordering(
        self,
        api_client: APIClient,
        injuries_treatment_factory: InjuriesTreatmentFactory,
    ):
        injuries_treatment_factory.create(name="Laser")
        injuries_treatment_factory.create(name="Cirurgia excisional")
        injuries_treatment_factory.create(name="Crioterapia")
        url = reverse("injuries-treatment-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        names = [item["name"] for item in resp.data]
        assert names == sorted(names)
