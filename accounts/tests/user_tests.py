import pytest
from django.urls import reverse
from pytest_factoryboy import register
from .factories import UserFactory

register(UserFactory)

@pytest.mark.django_db
class TestUserAPI:
    def test_list(self, api_client, user_factory):
        user_factory.create_batch(3)
        url = reverse("user-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 3

    def test_create(self, api_client, user_factory):
        new_user = user_factory.build()
        url = reverse("user-list")
        resp = api_client.post(url, data={
            "cpf": new_user.cpf,
            "name": new_user.name,
            "email": new_user.email,
            "password": new_user.password,
        })
        assert resp.status_code == 201
        assert resp.data["cpf"] == new_user.cpf
        assert resp.data["email"] == new_user.email

