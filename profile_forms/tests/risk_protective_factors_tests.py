import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.risk_protective_factors import (
    SunExposurePeriod,
    SunBurnHistory,
    UVProtectionSPF,
    CheckupsFrequency,
)
from .factories import UserFactory, RiskProtectiveFactorsFactory


register(UserFactory)
register(RiskProtectiveFactorsFactory)


@pytest.mark.django_db(transaction=True)
class TestRiskProtectiveFactorsAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse(
            "patient-risk-protective-factors-list", kwargs={"user_pk": user.id}
        )
        payload = {
            "sun_exposure_period": SunExposurePeriod.DAILY,
            "sun_burn": SunBurnHistory.NEVER,
            "uv_protection": UVProtectionSPF.SPF_50,
            "hat_use": True,
            "artifitial_tan": False,
            "checkups_frequency": CheckupsFrequency.ANNUALLY,
            "cancer_campaigns": True,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id
        assert res.data["hat_use"] is True
        assert res.data["artifitial_tan"] is False

    def test_duplicate_for_same_user(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse(
            "patient-risk-protective-factors-list", kwargs={"user_pk": user.id}
        )
        payload = {
            "sun_exposure_period": SunExposurePeriod.OCCASIONALLY,
            "sun_burn": SunBurnHistory.ONCE_TWICE,
            "uv_protection": UVProtectionSPF.NONE,
            "hat_use": False,
            "artifitial_tan": False,
            "checkups_frequency": CheckupsFrequency.NOT_REGULARLY,
            "cancer_campaigns": False,
        }
        first = api_client.post(url, payload, format="json")
        assert first.status_code == 201
        second = api_client.post(url, payload, format="json")
        assert second.status_code == 403

    def test_retrieve(
        self,
        api_client: APIClient,
        risk_protective_factors_factory: RiskProtectiveFactorsFactory,
    ):
        obj = risk_protective_factors_factory.create()
        url = reverse(
            "patient-risk-protective-factors-list", kwargs={"user_pk": obj.user.id}
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
        assert res.data["user"] == obj.user.id
