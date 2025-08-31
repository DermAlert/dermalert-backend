import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_forms.enums.cancer import Asymmetry, Border, ColorVariation, Diameter, Evolution
from skin_forms.tests.factories import SkinConditionFactory, CancerFactory


@pytest.mark.django_db(transaction=True)
class TestCancerNestedAPI:
    def create_skin_condition(self, user):
        return SkinConditionFactory(user=user)

    def test_create_and_list(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        url = reverse(
            "skin-condition-cancer-list",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id},
        )
        payload = {
            "asymmetry": Asymmetry.SYMMETRIC,
            "border": Border.REGULAR_WELL_DEFINED,
            "color_variation": ColorVariation.SINGLE_COLOR,
            "diameter": Diameter.UNDER_6MM,
            "evolution": Evolution.NO_CHANGES,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201, res.data

        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve_and_update(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        obj = CancerFactory(skin_condition=sc)
        url_detail = reverse(
            "skin-condition-cancer-detail",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id, "pk": obj.id},
        )

        res_get = api_client.get(url_detail)
        assert res_get.status_code == 200
        assert res_get.data["id"] == obj.id

        res_patch = api_client.patch(url_detail, {"evolution": Evolution.RECENT_CHANGES}, format="json")
        assert res_patch.status_code == 200
        assert res_patch.data["evolution"] == Evolution.RECENT_CHANGES
