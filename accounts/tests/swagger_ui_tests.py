import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestSwaggerUI:
    def test_swagger_ui_uses_custom_login_helper(self, client):
        response = client.get(reverse("schema-swagger-ui"))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-swagger-login-url="/api/v1/auth/login/"' in content
        assert 'id="swagger-login-modal"' in content
        assert "Sign in with CPF and password" in content
        assert "function loginWithCpfPassword()" in content

    def test_swagger_schema_exposes_token_security_definition(self, client):
        response = client.get(reverse("schema-json", kwargs={"format": ".json"}))

        assert response.status_code == 200
        payload = response.json()
        assert payload["securityDefinitions"]["Token"]["type"] == "apiKey"
        assert payload["securityDefinitions"]["Token"]["name"] == "Authorization"

    def test_swagger_schema_keeps_professional_management_paths(self, client):
        response = client.get(reverse("schema-json", kwargs={"format": ".json"}))

        assert response.status_code == 200
        paths = response.json()["paths"].keys()
        assert any("professional-assignments" in path for path in paths)
        assert any("professionals" in path for path in paths)
        assert any("managers" in path for path in paths)

    def test_swagger_schema_documents_auth_request_bodies(self, client):
        response = client.get(reverse("schema-json", kwargs={"format": ".json"}))

        assert response.status_code == 200
        paths = response.json()["paths"]

        change_email_path = next(
            path for path in paths.keys() if path.endswith("/auth/change-email/")
        )
        login_path = next(path for path in paths.keys() if path.endswith("/auth/login/"))
        wound_calculate_path = next(
            path for path in paths.keys() if path.endswith("/wounds/calculate/")
        )

        assert any(
            parameter["in"] == "body"
            for parameter in paths[change_email_path]["post"]["parameters"]
        )
        assert any(
            parameter["in"] == "body"
            for parameter in paths[login_path]["post"]["parameters"]
        )
        assert any(
            parameter["in"] == "body"
            for parameter in paths[wound_calculate_path]["post"]["parameters"]
        )
