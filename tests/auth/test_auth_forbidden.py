import logging

import pytest
from fastapi.testclient import TestClient

from fastapi_archetype.auth.dependencies import get_auth_functions
from fastapi_archetype.main import app

from .conftest import mock_auth_functions_reader_principal

AUTH_DEPS_LOGGER = "fastapi_archetype.auth.dependencies"


class TestForbiddenSanitization:
    def test_forbidden_does_not_reveal_role_name(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_functions] = (
            mock_auth_functions_reader_principal
        )
        try:
            response = entra_client.post(
                "/test/admin-required",
                json={"value": "X"},
                headers={"Authorization": "Bearer valid-token"},
            )
            assert response.status_code == 403
            body = response.json()
            assert body["errorCode"] == "FORBIDDEN"
            assert body["message"] == "Access forbidden"
            assert body["detail"] is None
            assert "admin" not in str(body).lower()
        finally:
            app.dependency_overrides.pop(get_auth_functions, None)

    def test_role_failure_logged_at_warning(
        self, entra_client: TestClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        app.dependency_overrides[get_auth_functions] = (
            mock_auth_functions_reader_principal
        )
        try:
            with caplog.at_level(logging.WARNING, logger=AUTH_DEPS_LOGGER):
                entra_client.post(
                    "/test/admin-required",
                    json={"value": "X"},
                    headers={"Authorization": "Bearer valid-token"},
                )
            warning_records = [
                r
                for r in caplog.records
                if r.levelno == logging.WARNING and r.name == AUTH_DEPS_LOGGER
            ]
            assert len(warning_records) >= 1
            assert "admin" in warning_records[0].message
        finally:
            app.dependency_overrides.pop(get_auth_functions, None)
