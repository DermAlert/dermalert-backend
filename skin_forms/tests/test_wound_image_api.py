import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_conditions.enums import BodySite
from skin_conditions.models import SkinCondition
from skin_forms.enums.wound import DepthOfTissueInjury, ExudateType, WoundBedTissue, WoundEdges
from skin_forms.models import Wound, WoundImage


def make_image_file(name="test.png", size=(16, 16), color=(155, 0, 0)):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, "PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


@pytest.mark.django_db(transaction=True)
class TestWoundImageNestedAPI:
    def create_wound(self, user):
        sc = SkinCondition.objects.create(user=user, location=BodySite.FACE, description="test")
        return Wound.objects.create(
            skin_condition=sc,
            height_mm=10,
            width_mm=10,
            wound_edges=WoundEdges.NO_EDGES,
            wound_bed_tissue=WoundBedTissue.REGENERATED_SCARRED,
            depth_of_tissue_injury=DepthOfTissueInjury.INTACT_SKIN,
            exudate_type=ExudateType.DRY,
        )

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
        image = make_image_file()
        res = api_client.post(url, {"image": image}, format="multipart")
        assert res.status_code == 201, res.data
        assert WoundImage.objects.count() == 1
        res_list = api_client.get(url)
        assert res_list.status_code == 200
        assert len(res_list.data) == 1

    def test_retrieve(self, api_client: APIClient):
        user = UserFactory()
        wound = self.create_wound(user)
        img = WoundImage.objects.create(wound=wound, image=make_image_file("a.png"))
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
