import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite, SkinConditionType
from skin_conditions.models import SkinCondition
from .factories import SkinConditionFactory
from skin_forms.tests.factories import WoundFactory, CancerFactory


register(UserFactory)


@pytest.mark.django_db(transaction=True)
class TestSkinConditionAPI:
    def test_create_and_list(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url_list = reverse("patient-skin-conditions-list", kwargs={"user_pk": user.id})
        payload = {"location": BodySite.FACE, "type": SkinConditionType.WOUND}
        res = api_client.post(url_list, payload, format="json")
        assert res.status_code == 201
        res_list = api_client.get(url_list)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve_includes_nested_forms(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        skin_condition = SkinConditionFactory(user=user)

        # Create related nested objects
        wound = WoundFactory(skin_condition=skin_condition)
        cancer = CancerFactory(skin_condition=skin_condition)

        url_detail = reverse(
            "patient-skin-conditions-detail",
            kwargs={"user_pk": user.id, "pk": skin_condition.id},
        )
        res = api_client.get(url_detail)
        assert res.status_code == 200
        assert res.data["id"] == skin_condition.id

        # Nested arrays present and contain the created items
        assert "wounds" in res.data
        assert "cancer_forms" in res.data
        assert isinstance(res.data["wounds"], list)
        assert isinstance(res.data["cancer_forms"], list)
        assert len(res.data["wounds"]) == 1
        assert len(res.data["cancer_forms"]) == 1

        # Sanity check: fields inside nested items
        assert res.data["wounds"][0]["id"] == wound.id
        assert res.data["cancer_forms"][0]["id"] == cancer.id
