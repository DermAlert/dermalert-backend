import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.lifestyle_risk import YesNo
from .factories import UserFactory, CareAccessSupportFactory


register(UserFactory)
register(CareAccessSupportFactory)


@pytest.mark.django_db(transaction=True)
class TestCareAccessSupportAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-care-access-support-list", kwargs={"user_pk": user.id})
        payload = {
            "has_dressings_available": YesNo.YES,
            "has_help_at_home": YesNo.NO,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id

    def test_duplicate_for_same_user(
        self,
        api_client: APIClient,
        care_access_support_factory: CareAccessSupportFactory,
    ):
        obj = care_access_support_factory.create()
        url = reverse(
            "patient-care-access-support-list", kwargs={"user_pk": obj.user.id}
        )
        payload = {
            "has_dressings_available": YesNo.NO,
            "has_help_at_home": YesNo.NO,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 403

    def test_retrieve(
        self,
        api_client: APIClient,
        care_access_support_factory: CareAccessSupportFactory,
    ):
        obj = care_access_support_factory.create()
        url = reverse(
            "patient-care-access-support-list", kwargs={"user_pk": obj.user.id}
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
        assert res.data["user"] == obj.user.id
