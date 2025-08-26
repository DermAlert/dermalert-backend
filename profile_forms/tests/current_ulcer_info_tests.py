import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.cancer_research import HowLong
from profile_forms.enums.clinical_history import YesNoUnknown
from profile_forms.enums.current_ulcer_info import UlcerTreatmentPlace
from .factories import UserFactory, CurrentUlcerInfoFactory


register(UserFactory)
register(CurrentUlcerInfoFactory)


@pytest.mark.django_db(transaction=True)
class TestCurrentUlcerInfoAPI:
    def test_create_basic(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("patient-current-ulcer-info-list", kwargs={"user_pk": user.id})
        payload = {
            "how_long": HowLong.THREE_TO_SIX_MONTHS,
            "treated_elsewhere": UlcerTreatmentPlace.UBS,
            "used_antibiotics": YesNoUnknown.DONT_KNOW,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        assert res.data["user"] == user.id

    def test_duplicate_for_same_user(
        self, api_client: APIClient, current_ulcer_info_factory: CurrentUlcerInfoFactory
    ):
        obj = current_ulcer_info_factory.create()
        url = reverse(
            "patient-current-ulcer-info-list", kwargs={"user_pk": obj.user.id}
        )
        payload = {
            "how_long": HowLong.LESS_THAN_ONE_MONTH,
            "treated_elsewhere": UlcerTreatmentPlace.NONE,
            "used_antibiotics": YesNoUnknown.NO,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 403

    def test_retrieve(
        self, api_client: APIClient, current_ulcer_info_factory: CurrentUlcerInfoFactory
    ):
        obj = current_ulcer_info_factory.create()
        url = reverse(
            "patient-current-ulcer-info-list", kwargs={"user_pk": obj.user.id}
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == obj.id
        assert res.data["user"] == obj.user.id
