import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.clinical_history import YesNoUnknown, CompressionStockingsUse
from .factories import UserFactory, ClinicalHistoryFactory


register(UserFactory)
register(ClinicalHistoryFactory)


@pytest.mark.django_db(transaction=True)
class TestClinicalHistoryAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-clinical-history-list", kwargs={"user_pk": user.id})
        payload = {
            "hypertension": YesNoUnknown.YES,
            "diabetes": YesNoUnknown.NO,
            "deep_vein_thrombosis": YesNoUnknown.DONT_KNOW,
            "chronic_venous_insufficiency": YesNoUnknown.NO,
            "compression_stockings_use": CompressionStockingsUse.CURRENTLY,
            "description": "Initial clinical history",
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id
        assert res.data["hypertension"] == YesNoUnknown.YES
        assert (
            res.data["compression_stockings_use"] == CompressionStockingsUse.CURRENTLY
        )

    def test_duplicate_for_same_user(
        self,
        api_client: APIClient,
        user_factory: UserFactory,
        clinical_history_factory: ClinicalHistoryFactory,
    ):
        ch = clinical_history_factory.create()
        url = reverse("patient-clinical-history-list", kwargs={"user_pk": ch.user.id})
        payload = {
            "hypertension": YesNoUnknown.NO,
            "diabetes": YesNoUnknown.NO,
            "deep_vein_thrombosis": YesNoUnknown.NO,
            "chronic_venous_insufficiency": YesNoUnknown.NO,
            "compression_stockings_use": CompressionStockingsUse.NEVER_USED,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 403

    def test_retrieve(
        self, api_client: APIClient, clinical_history_factory: ClinicalHistoryFactory
    ):
        ch = clinical_history_factory.create(
            hypertension=YesNoUnknown.NO,
            diabetes=YesNoUnknown.YES,
            deep_vein_thrombosis=YesNoUnknown.NO,
            chronic_venous_insufficiency=YesNoUnknown.DONT_KNOW,
            compression_stockings_use=CompressionStockingsUse.USED_BUT_NOT_ANYMORE,
        )
        url = reverse("patient-clinical-history-list", kwargs={"user_pk": ch.user.id})
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["diabetes"] == YesNoUnknown.YES
        assert (
            res.data["compression_stockings_use"]
            == CompressionStockingsUse.USED_BUT_NOT_ANYMORE
        )
