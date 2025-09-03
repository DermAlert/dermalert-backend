import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_forms.models import WoundImage
from skin_forms.tests.factories import WoundFactory, WoundImageFactory


@pytest.mark.django_db(transaction=True)
class TestWoundImageNestedAPI:
    def create_wound(self, user):
        return WoundFactory(skin_condition__user=user)

    def test_upload_and_list(self, api_client: APIClient):
        user = UserFactory()
        wound = self.create_wound(user)
        url = reverse(
            "wound-images-list",
            kwargs={
                "user_pk": user.id,
                "skin_condition_pk": wound.skin_condition_id,
                "wound_pk": wound.id,
            },
        )
        res = api_client.post(
            url, {"image": WoundImageFactory.build().image}, format="multipart"
        )
        assert res.status_code == 201, res.data
        assert WoundImage.objects.count() == 1
        # verifica que a URL da imagem está presente e com prefixo esperado
        assert "image" in res.data and isinstance(res.data["image"], str)
        assert "/wound_images/" in res.data["image"]
        if getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None):
            expected_prefix = f"{settings.AWS_S3_URL_PROTOCOL}//{settings.AWS_S3_CUSTOM_DOMAIN}"
            assert res.data["image"].startswith(expected_prefix)
        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1
        assert "image" in res_list.data[0] and "/wound_images/" in res_list.data[0]["image"]

    def test_retrieve(self, api_client: APIClient):
        user = UserFactory()
        wound = self.create_wound(user)
        img = WoundImageFactory(wound=wound)
        url = reverse(
            "wound-images-detail",
            kwargs={
                "user_pk": user.id,
                "skin_condition_pk": wound.skin_condition_id,
                "wound_pk": wound.id,
                "pk": img.id,
            },
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == img.id
        assert "image" in res.data and "/wound_images/" in res.data["image"]
