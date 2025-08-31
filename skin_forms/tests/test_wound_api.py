import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_forms.tests.factories import SkinConditionFactory, WoundFactory
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
        return SkinConditionFactory(user=user)

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
        # height=20mm=>2cm, width=30mm=>3cm, area=6cm^2 => item1=2
        # item2=1 (EPIDERMIS_DERMIS), item3=2, item4=2, item5=0, item6=0 => total=7
        assert res.data["total_score"] == 7

        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        wound = WoundFactory(skin_condition=sc)
        url = reverse(
            "skin-condition-wounds-detail",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id, "pk": wound.id},
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == wound.id

    def test_negative_dimensions_fail(self, api_client: APIClient):
        user = UserFactory()
        sc = self.create_skin_condition(user)
        url = reverse(
            "skin-condition-wounds-list",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc.id},
        )
        payload = {
            "height_mm": -1,
            "width_mm": 10,
            "wound_edges": WoundEdges.NO_EDGES,
            "wound_bed_tissue": WoundBedTissue.REGENERATED_SCARRED,
            "depth_of_tissue_injury": DepthOfTissueInjury.INTACT_SKIN,
            "exudate_type": ExudateType.DRY,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 400

    def test_skin_condition_from_url_ignored_in_payload(self, api_client: APIClient):
        user = UserFactory()
        sc1 = self.create_skin_condition(user)
        sc2 = self.create_skin_condition(user)
        url = reverse(
            "skin-condition-wounds-list",
            kwargs={"user_pk": user.id, "skin_condition_pk": sc1.id},
        )
        payload = {
            "skin_condition": sc2.id,  # should be ignored (read-only)
            "height_mm": 10,
            "width_mm": 10,
            "wound_edges": WoundEdges.NO_EDGES,
            "wound_bed_tissue": WoundBedTissue.REGENERATED_SCARRED,
            "depth_of_tissue_injury": DepthOfTissueInjury.INTACT_SKIN,
            "exudate_type": ExudateType.DRY,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        w = Wound.objects.get(id=res.data["id"])
        assert w.skin_condition_id == sc1.id
