import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_forms.models import CancerImage
from skin_forms.tests.factories import CancerFactory, CancerImageFactory


@pytest.mark.django_db(transaction=True)
class TestCancerImageNestedAPI:
    def test_upload_and_list(self, api_client: APIClient):
        user = UserFactory()
        cancer = CancerFactory(skin_condition__user=user)
        url = reverse(
            "cancer-images-list",
            kwargs={
                "user_pk": user.id,
                "skin_condition_pk": cancer.skin_condition_id,
                "cancer_pk": cancer.id,
            },
        )
        res = api_client.post(
            url, {"image": CancerImageFactory.build().image}, format="multipart"
        )
        assert res.status_code == 201, res.data
        assert CancerImage.objects.count() == 1
        assert "image" in res.data and isinstance(res.data["image"], str)
        assert "/cancer_images/" in res.data["image"]
        if getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None):
            expected_prefix = f"{settings.AWS_S3_URL_PROTOCOL}//{settings.AWS_S3_CUSTOM_DOMAIN}"
            assert res.data["image"].startswith(expected_prefix)
        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1
        assert "image" in res_list.data[0] and "/cancer_images/" in res_list.data[0]["image"]

    def test_retrieve(self, api_client: APIClient):
        user = UserFactory()
        cancer = CancerFactory(skin_condition__user=user)
        img = CancerImageFactory(cancer=cancer)
        url = reverse(
            "cancer-images-detail",
            kwargs={
                "user_pk": user.id,
                "skin_condition_pk": cancer.skin_condition_id,
                "cancer_pk": cancer.id,
                "pk": img.id,
            },
        )
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["id"] == img.id
        assert "image" in res.data and "/cancer_images/" in res.data["image"]
