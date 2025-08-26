import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.lifestyle_risk import (
    LongPeriodsPosture,
    YesNo,
    SmokingStatus,
)
from .factories import UserFactory, LifestyleRiskFactory


register(UserFactory)
register(LifestyleRiskFactory)


@pytest.mark.django_db(transaction=True)
class TestLifestyleRiskAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-lifestyle-risk-list", kwargs={"user_pk": user.id})
        payload = {
            "long_periods_posture": LongPeriodsPosture.SITTING_LONG_HOURS,
            "leg_foot_trauma": YesNo.NO,
            "smoking": SmokingStatus.FORMER_SMOKER,
            "physical_activity": YesNo.YES,
            "description": "Risk and lifestyle",
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id
        assert res.data["physical_activity"] == YesNo.YES

    def test_duplicate_for_same_user(
        self, api_client: APIClient, lifestyle_risk_factory: LifestyleRiskFactory
    ):
        obj = lifestyle_risk_factory.create()
        url = reverse("patient-lifestyle-risk-list", kwargs={"user_pk": obj.user.id})
        payload = {
            "long_periods_posture": LongPeriodsPosture.NO,
            "leg_foot_trauma": YesNo.NO,
            "smoking": SmokingStatus.NEVER_SMOKED,
            "physical_activity": YesNo.NO,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 403

    def test_retrieve(
        self, api_client: APIClient, lifestyle_risk_factory: LifestyleRiskFactory
    ):
        obj = lifestyle_risk_factory.create(
            long_periods_posture=LongPeriodsPosture.STANDING_LONG_HOURS,
            leg_foot_trauma=YesNo.YES,
            smoking=SmokingStatus.CURRENT_SMOKER,
            physical_activity=YesNo.NO,
        )
        url = reverse("patient-lifestyle-risk-list", kwargs={"user_pk": obj.user.id})
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
        assert res.data["user"] == obj.user.id
