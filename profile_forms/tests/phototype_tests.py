import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profile_forms.enums.phototype import (
    SkinColor,
    EyesColor,
    HairColor,
    FrecklesAmount,
    SunExposureReaction,
    TannedSkinAbility,
    SunSensitivityFace,
    PhototypeClass,
)
from profile_forms.models import Phototype
from .factories import UserFactory, PhototypeFactory


register(UserFactory)
register(PhototypeFactory)


@pytest.mark.django_db(transaction=True)
class TestPhototypeAPI:
    def test_create_min_scores_class_I(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-phototype-list", kwargs={"user_pk": user.id})
        payload = {
            "skin_color": SkinColor.MILKY_WHITE,
            "eyes_color": EyesColor.LIGHT_BLUE_GRAY_GREEN,
            "hair_color": HairColor.RED_LIGHT_BLOND,
            "freckles": FrecklesAmount.MANY,
            "sun_exposed": SunExposureReaction.ALWAYS_BURNS_PEELS_PAINFUL,
            "tanned_skin": TannedSkinAbility.NEVER_ALWAYS_BURNS,
            "sun_sensitive_skin": SunSensitivityFace.VERY_SENSITIVE,
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        obj = Phototype.objects.get(user=user)
        assert obj.phototype == PhototypeClass.I
        assert obj.score == 0

    def test_create_mid_scores_class_III(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-phototype-list", kwargs={"user_pk": user.id})
        payload = {
            # 8 + 2 + 2 + 2 + 4 + 4 + 2 = 24 -> Class III (17-25)
            "skin_color": SkinColor.BEIGE,  # 8
            "eyes_color": EyesColor.BLUE_GRAY_GREEN,  # 1 (ajustaremos abaixo para fechar 24)
            "hair_color": HairColor.BROWN,  # 2
            "freckles": FrecklesAmount.FEW,  # 2
            "sun_exposed": SunExposureReaction.BURNS_NO_PEEL,  # 4
            "tanned_skin": TannedSkinAbility.OFTEN,  # 4
            "sun_sensitive_skin": SunSensitivityFace.NORMAL,  # 2
        }
        # Corrige olhos para 3 pontos e chegar no range 23-25
        payload["eyes_color"] = EyesColor.LIGHT_BROWN  # 3
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        obj = Phototype.objects.get(user=user)
        assert obj.phototype == PhototypeClass.III
        assert 17 <= obj.score <= 25

    def test_create_high_scores_class_IV(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-phototype-list", kwargs={"user_pk": user.id})
        payload = {
            # 16 + 4 + 4 + 3 + 8 + 6 + 4 = 45 -> Class V/VI (>40) mas vamos ajustar para 26-30
            # Ajuste para ficar em ~28: 12 + 2 + 3 + 2 + 6 + 4 + 1 = 30 -> Class IV
            "skin_color": SkinColor.LIGHT_BROWN,  # 12
            "eyes_color": EyesColor.BLUE,  # 2
            "hair_color": HairColor.DARK_BROWN,  # 3
            "freckles": FrecklesAmount.FEW,  # 2
            "sun_exposed": SunExposureReaction.SELDOM_OR_NOT_RED,  # 6
            "tanned_skin": TannedSkinAbility.OFTEN,  # 4
            "sun_sensitive_skin": SunSensitivityFace.SENSITIVE,  # 1
        }
        res = api_client.post(url, payload, format="json")
        assert res.status_code == 201
        obj = Phototype.objects.get(user=user)
        assert obj.phototype == PhototypeClass.IV
        assert 26 <= obj.score <= 30

    def test_create_duplicate_for_same_user(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("patient-phototype-list", kwargs={"user_pk": user.id})
        payload = {
            "skin_color": SkinColor.WHITE,
            "eyes_color": EyesColor.BLUE,
            "hair_color": HairColor.BROWN,
            "freckles": FrecklesAmount.SOME,
            "sun_exposed": SunExposureReaction.BURNS_PEELS_A_LITTLE,
            "tanned_skin": TannedSkinAbility.SOMETIMES,
            "sun_sensitive_skin": SunSensitivityFace.NORMAL,
        }
        first = api_client.post(url, payload, format="json")
        assert first.status_code == 201
        second = api_client.post(url, payload, format="json")
        assert second.status_code == 403

    def test_retrieve(self, api_client: APIClient, phototype_factory: PhototypeFactory):
        pt = phototype_factory.create()
        url = reverse("patient-phototype-list", kwargs={"user_pk": pt.user.id})
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == pt.id
        assert res.data["user"] == pt.user.id
