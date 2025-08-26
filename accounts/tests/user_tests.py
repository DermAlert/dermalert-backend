import pytest
from django.urls import reverse
from pytest_factoryboy import register
from rest_framework.test import APIClient
from .factories import UserFactory
from accounts.models import User

register(UserFactory)


@pytest.mark.django_db
class TestUserAPI:
    def test_list(self, api_client: APIClient, user_factory: UserFactory):
        user_factory.create_batch(3)
        url = reverse("user-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 3

    def test_create(self, api_client: APIClient, user_factory: UserFactory):
        new_user = user_factory.build()
        url = reverse("user-list")
        resp = api_client.post(
            url,
            data={
                "cpf": new_user.cpf,
                "name": new_user.name,
                "email": new_user.email,
                "password": new_user.password,
            },
        )
        assert resp.status_code == 201
        assert resp.data["cpf"] == new_user.cpf
        assert resp.data["email"] == new_user.email

    def test_retrieve(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("user-detail", kwargs={"pk": user.id})
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["cpf"] == user.cpf
        assert resp.data["email"] == user.email

    def test_update(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("user-detail", kwargs={"pk": user.id})
        resp = api_client.patch(url, data={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.data["name"] == "Updated Name"
        assert resp.data["cpf"] == user.cpf

    def test_delete(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        url = reverse("user-detail", kwargs={"pk": user.id})
        resp = api_client.delete(url)
        assert resp.status_code == 204
        assert not User.objects.filter(id=user.id).exists()

    def test_invalid_cpf_validation(self, api_client: APIClient):
        url = reverse("user-list")
        resp = api_client.post(
            url,
            data={
                "cpf": "123",  # Invalid: not 11 digits
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 400
        assert "cpf" in resp.data

    def test_filter_by_cpf(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        other_user = user_factory.create()
        assert user.cpf != other_user.cpf

        url = f"{reverse('user-list')}?cpf={user.cpf}"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["cpf"] == user.cpf

    def test_filter_by_name(self, api_client: APIClient, user_factory: UserFactory):
        user = user_factory.create()
        other_user = user_factory.create()
        assert user.name != other_user.name

        url = f"{reverse('user-list')}?name={user.name}"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["name"] == user.name

    def test_create_user_with_existing_cpf(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("user-list")
        resp = api_client.post(
            url,
            data={
                "cpf": user.cpf,
                "name": "New User",
                "email": "newuser@email.com",
                "password": "newpassword",
            },
        )
        assert resp.status_code == 400
        assert User.objects.filter(email="newuser@email.com").exists() == False
        assert User.objects.filter(email=user.email).exists() == True

    def test_update_user_with_existing_cpf(
        self, api_client: APIClient, user_factory: UserFactory
    ):
        user = user_factory.create()
        url = reverse("user-detail", kwargs={"pk": user.id})
        resp = api_client.patch(
            url,
            data={
                "cpf": user.cpf,  # Trying to update with the same CPF
                "name": "Updated Name",
                "email": "newemail@email.com",
            },
        )
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.name == "Updated Name"
        assert user.email == "newemail@email.com"
