import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite
from skin_conditions.models import SkinCondition
from skin_forms.enums.wound import (
    DepthOfTissueInjury,
    ExudateType,
    WoundBedTissue,
    WoundEdges,
)
from skin_forms.models import Wound


@pytest.mark.django_db(transaction=True)
class TestWoundNestedAPI:
    def create_skin_condition(self, user):
        return SkinCondition.objects.create(
            user=user, location=BodySite.FACE, description="test"
        )

    def test_create_and_list(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        url = reverse(
            "skin-condition-wounds-list",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id},
        )
        payload = {
            "height_mm": 20,
            "width_mm": 30,
            "wound_edges": WoundEdges.WELL_DEFINED,
            "wound_bed_tissue": WoundBedTissue.GRANULATION,
            "depth_of_tissue_injury": DepthOfTissueInjury.EPIDERMIS_DERMIS,
            "exudate_type": ExudateType.MOIST,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert "total_score" in res.data

        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        wound = Wound.objects.create(
            skin_condition=sc,
            height_mm=10,
            width_mm=10,
            wound_edges=WoundEdges.NO_EDGES,
            wound_bed_tissue=WoundBedTissue.REGENERATED_SCARRED,
            depth_of_tissue_injury=DepthOfTissueInjury.INTACT_SKIN,
            exudate_type=ExudateType.DRY,
        )
        url = reverse(
            "skin-condition-wounds-detail",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id, "pk": wound.id},
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == wound.id
