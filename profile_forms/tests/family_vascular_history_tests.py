import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.clinical_history import YesNoUnknown
from .factories import UserFactory, FamilyVascularHistoryFactory


register(UserFactory)
register(FamilyVascularHistoryFactory)


@pytest.mark.django_db(transaction=True)
class TestFamilyVascularHistoryAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse(
            "patient-family-vascular-history-list", kwargs={"user_pk": user.id}
        )
        payload = {
            "family_leg_ulcers": YesNoUnknown.YES,
            "family_varicose_or_circulatory": YesNoUnknown.DONT_KNOW,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id

    def test_duplicate_for_same_user(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse(
            "patient-family-vascular-history-list", kwargs={"user_pk": user.id}
        )
        payload = {
            "family_leg_ulcers": YesNoUnknown.NO,
            "family_varicose_or_circulatory": YesNoUnknown.NO,
        }
        first = api_client.post(url, payload, format="json")
        assert first.status_code == 201
        second = api_client.post(url, payload, format="json")
        assert second.status_code == 403

    def test_retrieve(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse(
            "patient-family-vascular-history-list", kwargs={"user_pk": user.id}
        )
        payload = {
            "family_leg_ulcers": YesNoUnknown.NO,
            "family_varicose_or_circulatory": YesNoUnknown.YES,
        }
        self_created = api_client.post(url, payload, format="json")
        assert self_created.status_code == 201
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["id"] == self_created.data["id"]
        assert resp.data["user"] == user.id
