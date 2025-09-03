import io
from PIL import Image
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory
from consent_form.models import ConsentTerm, ConsentSignature


def make_image(color=(255, 0, 0)):
    file = io.BytesIO()
    img = Image.new("RGB", (20, 20), color)
    img.save(file, "PNG")
    file.name = "sig.png"
    file.seek(0)
    return file


@pytest.mark.django_db(transaction=True)
class TestConsentAPI:
    def test_latest_no_terms(self, api_client: APIClient):
        url = reverse("consent-terms-latest")
        res = api_client.get(url)
        assert res.status_code == 204

    def test_latest_with_terms(self, api_client: APIClient):
        ConsentTerm.objects.create(version=1, url="https://example.com/t1.pdf")
        ConsentTerm.objects.create(version=2, url="https://example.com/t2.pdf")
        url = reverse("consent-terms-latest")
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["version"] == 2

    def test_needs_signature_true(self, api_client: APIClient):
        user = UserFactory()
        term = ConsentTerm.objects.create(version=1, url="https://example.com/t1.pdf")
        url = reverse("patient-consent-needs-signature", kwargs={"user_pk": user.id})
        res = api_client.get(url)
        assert res.status_code == 200
        assert res.data["needs_signature"] is True

    def test_sign_and_needs_signature_false(self, api_client: APIClient):
        user = UserFactory()
        term = ConsentTerm.objects.create(version=3, url="https://example.com/t3.pdf")
        url_sign = reverse("patient-consent-sign", kwargs={"user_pk": user.id})
        payload = {
            "term": term.id,
            "has_signed": True,
            "images": [make_image(), make_image()],
        }
        res = api_client.post(url_sign, payload, format="multipart")
        assert res.status_code == 201
        # agora não precisa mais assinar a última
        url_check = reverse(
            "patient-consent-needs-signature", kwargs={"user_pk": user.id}
        )
        res2 = api_client.get(url_check)
        assert res2.status_code == 200
        assert res2.data["needs_signature"] is False

    def test_sign_duplicate_for_same_term(self, api_client: APIClient):
        user = UserFactory()
        term = ConsentTerm.objects.create(version=5, url="https://example.com/t5.pdf")
        url_sign = reverse("patient-consent-sign", kwargs={"user_pk": user.id})
        payload = {"term": term.id, "has_signed": True, "images": [make_image()]}
        first = api_client.post(url_sign, payload, format="multipart")
        assert first.status_code == 201
        second = api_client.post(url_sign, payload, format="multipart")
        assert second.status_code == 400
