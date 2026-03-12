import logging

import pytest
from fastapi.testclient import TestClient

from fastapi_archetype.auth.dependencies import get_auth_functions
from fastapi_archetype.main import app

from .conftest import (
    mock_auth_functions_unauthorized,
    mock_auth_functions_unexpected_error,
)

AUTH_DEPS_LOGGER = "fastapi_archetype.auth.dependencies"


class TestUnauthorizedSanitization:
    def test_missing_token_returns_generic_401(self, entra_client: TestClient) -> None:
        response = entra_client.get("/test/open")
        assert response.status_code == 200

        response = entra_client.post("/test/auth-required", json={"value": "X"})
        assert response.status_code == 401
        body = response.json()
        assert body["errorCode"] == "UNAUTHORIZED"
        assert body["message"] == "Authentication required"
        assert body["detail"] is None

    def test_malformed_token_does_not_leak_provider_details(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_functions] = mock_auth_functions_unauthorized
        try:
            response = entra_client.post(
                "/test/auth-required",
                json={"value": "X"},
                headers={"Authorization": "Bearer bad-token"},
            )
            assert response.status_code == 401
            body = response.json()
            assert body["errorCode"] == "UNAUTHORIZED"
            assert body["message"] == "Authentication required"
            assert body["detail"] is None
            assert "JWKS" not in str(body)
        finally:
            app.dependency_overrides.pop(get_auth_functions, None)

    def test_unexpected_error_does_not_leak_urls(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_functions] = (
            mock_auth_functions_unexpected_error
        )
        try:
            response = entra_client.post(
                "/test/auth-required",
                json={"value": "X"},
                headers={"Authorization": "Bearer some-token"},
            )
            assert response.status_code == 401
            body = response.json()
            assert body["detail"] is None
            assert "microsoftonline" not in str(body)
        finally:
            app.dependency_overrides.pop(get_auth_functions, None)

    def test_auth_failure_logged_at_warning(
        self, entra_client: TestClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        app.dependency_overrides[get_auth_functions] = mock_auth_functions_unauthorized
        try:
            with caplog.at_level(logging.WARNING, logger=AUTH_DEPS_LOGGER):
                entra_client.post(
                    "/test/auth-required",
                    json={"value": "X"},
                    headers={"Authorization": "Bearer bad"},
                )
            warning_records = [
                r
                for r in caplog.records
                if r.levelno == logging.WARNING and r.name == AUTH_DEPS_LOGGER
            ]
            assert len(warning_records) >= 1
            assert "JWKS" in warning_records[0].message
        finally:
            app.dependency_overrides.pop(get_auth_functions, None)
