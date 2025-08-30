import io

import pytest
from django.urls import reverse
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest_factoryboy import register

from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from skin_forms.models import Wound


register(UserFactory)


def make_test_image(filename: str = "img.jpg", size=(10, 10), color=(255, 0, 0)):
	buf = io.BytesIO()
	img = PILImage.new("RGB", size, color)
	img.save(buf, format="JPEG")
	buf.seek(0)
	return SimpleUploadedFile(filename, buf.read(), content_type="image/jpeg")


@pytest.mark.django_db(transaction=True)
class TestWoundAPI:
	def test_create_wound_with_multiple_images(self, api_client: APIClient):
		url = reverse("wound-list")
		payload = {
			"height_mm": 10,
			"width_mm": 20,
			"wound_edges": "no_edges",
			"wound_bed_tissue": "regenerated_scarred",
			"depth_of_tissue_injury": "intact_skin",
			"exudate_type": "dry",
			"increased_pain": False,
			"perilesional_erythema": False,
			"perilesional_edema": False,
			"heat_or_warm_skin": False,
			"increased_exudate": False,
			"purulent_exudate": False,
			"friable_tissue": False,
			"stagnant_wound": False,
			"biofilm_compatible_tissue": False,
			"odor": False,
			"hypergranulation": False,
			"wound_size_increase": False,
			"satallite_lesions": False,
			"grayish_wound_bed": False,
			"image_type": "photographic",
			"images": [make_test_image("a.jpg"), make_test_image("b.jpg")],
		}
		response = api_client.post(url, data=payload, format="multipart")
		assert response.status_code == 201
		wound_id = response.data["id"]
		assert len(response.data["attachments"]) == 2

		# Recupera detalhe e confere attachments
		detail = api_client.get(reverse("wound-detail", kwargs={"pk": wound_id}))
		assert detail.status_code == 200
		assert len(detail.data["attachments"]) == 2

	def test_upload_images_action(self, api_client: APIClient):
		# Cria um wound sem imagens
		url = reverse("wound-list")
		payload = {
			"height_mm": 5,
			"width_mm": 5,
			"wound_edges": "no_edges",
			"wound_bed_tissue": "regenerated_scarred",
			"depth_of_tissue_injury": "intact_skin",
			"exudate_type": "dry",
			"increased_pain": False,
			"perilesional_erythema": False,
			"perilesional_edema": False,
			"heat_or_warm_skin": False,
			"increased_exudate": False,
			"purulent_exudate": False,
			"friable_tissue": False,
			"stagnant_wound": False,
			"biofilm_compatible_tissue": False,
			"odor": False,
			"hypergranulation": False,
			"wound_size_increase": False,
			"satallite_lesions": False,
			"grayish_wound_bed": False,
		}
		res = api_client.post(url, payload, format="json")
		assert res.status_code == 201
		wound_id = res.data["id"]

		# Faz upload de 2 imagens via action
		action_url = reverse("wound-upload-images", kwargs={"pk": wound_id})
		payload = {
			"image_type": "dermoscopic",
			"images": [make_test_image("x.jpg"), make_test_image("y.jpg")],
		}
		up = api_client.post(action_url, data=payload, format="multipart")
		assert up.status_code == 201
		assert len(up.data) == 2

		# Detalhe deve agora ter 2 attachments
		detail = api_client.get(reverse("wound-detail", kwargs={"pk": wound_id}))
		assert detail.status_code == 200
		assert len(detail.data["attachments"]) == 2
