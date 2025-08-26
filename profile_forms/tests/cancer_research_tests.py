import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.cancer_research import HowLong
from .factories import UserFactory, CancerResearchFactory


register(UserFactory)
register(CancerResearchFactory)


@pytest.mark.django_db(transaction=True)
class TestCancerResearchAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-cancer-research-list", kwargs={"user_pk": user.id})
        payload = {
            "suspicious_moles": True,
            "bleed_itch": False,
            "how_long": HowLong.ONE_TO_THREE_MONTHS,
            "lesion_aspect": True,
            "doctor_assistance": True,
            "diagnosis": "Benign nevus",
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id
        assert res.data["diagnosis"] == "Benign nevus"

    def test_duplicate_for_same_user(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-cancer-research-list", kwargs={"user_pk": user.id})
        payload = {
            "suspicious_moles": False,
            "bleed_itch": False,
            "how_long": HowLong.LESS_THAN_ONE_MONTH,
            "lesion_aspect": False,
            "doctor_assistance": False,
            "diagnosis": "",
        }
        first = api_client.post(url, payload, format="json")
        assert first.status_code == 201
        second = api_client.post(url, payload, format="json")
        assert second.status_code == 403

    def test_retrieve(self, api_client: APIClient, cancer_research_factory: CancerResearchFactory):
        obj = cancer_research_factory.create()
        url = reverse("patient-cancer-research-list", kwargs={"user_pk": obj.user.id})
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
        assert res.data["user"] == obj.user.id
