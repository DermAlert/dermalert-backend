import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite
from skin_conditions.models import SkinCondition


register(UserFactory)


@pytest.mark.django_db(transaction=True)
class TestSkinConditionAPI:
    def test_create_and_list(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url_list = reverse("patient-skin-conditions-list", kwargs={"user_pk": user.id})
        payload = {"location": BodySite.FACE, "description": "Small lesion"}
        res = api_client.post(url_list, payload, format="json")
        assert res.status_code == 201
        res_list = api_client.get(url_list)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        obj = SkinCondition.objects.create(
            user=user, location=BodySite.HAND, description="Test"
        )
        url_detail = reverse(
            "patient-skin-conditions-detail",
            kwargs={"user_pk": user.id, "pk": obj.id},
        )
        res = api_client.get(url_detail)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
