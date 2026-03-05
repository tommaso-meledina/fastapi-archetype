from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.contracts import UnauthorizedError
from fastapi_archetype.auth.dependencies import get_auth_facade
from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.models import Principal
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app

if TYPE_CHECKING:
    from collections.abc import Generator

AUTH_DEPS_LOGGER = "fastapi_archetype.auth.dependencies"


@pytest.fixture(name="_entra_engine", scope="module")
def entra_engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(name="entra_client")
def entra_client_fixture(_entra_engine) -> Generator[TestClient]:
    """Client with auth_type patched to 'entra' so auth-error paths execute."""

    def _override_session():
        with Session(_entra_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    limiter.reset()

    with (
        patch(
            "fastapi_archetype.auth.dependencies._settings.auth_type",
            "entra",
        ),
        TestClient(app) as c,
    ):
        yield c

    app.dependency_overrides.clear()


def _mock_facade_unauthorized() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.side_effect = UnauthorizedError(
        "JWKS endpoint did not return a valid keys list"
    )
    return facade


def _mock_facade_unexpected_error() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.side_effect = RuntimeError(
        "https://login.microsoftonline.com/.well-known/openid-configuration"
    )
    return facade


def _mock_facade_reader_principal() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.return_value = Principal(
        subject="user-1",
        user_id="user-1",
        name="Test User",
        roles=["reader"],
    )
    return facade


class TestUnauthorizedSanitization:
    def test_missing_token_returns_generic_401(self, entra_client: TestClient) -> None:
        response = entra_client.get("/v1/dummies")
        assert response.status_code == 200

        response = entra_client.post("/v1/dummies", json={"name": "X"})
        assert response.status_code == 401
        body = response.json()
        assert body["errorCode"] == "UNAUTHORIZED"
        assert body["message"] == "Authentication required"
        assert body["detail"] is None

    def test_malformed_token_does_not_leak_provider_details(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_facade] = _mock_facade_unauthorized
        try:
            response = entra_client.post(
                "/v1/dummies",
                json={"name": "X"},
                headers={"Authorization": "Bearer bad-token"},
            )
            assert response.status_code == 401
            body = response.json()
            assert body["errorCode"] == "UNAUTHORIZED"
            assert body["message"] == "Authentication required"
            assert body["detail"] is None
            assert "JWKS" not in str(body)
        finally:
            app.dependency_overrides.pop(get_auth_facade, None)

    def test_unexpected_error_does_not_leak_urls(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_facade] = _mock_facade_unexpected_error
        try:
            response = entra_client.post(
                "/v1/dummies",
                json={"name": "X"},
                headers={"Authorization": "Bearer some-token"},
            )
            assert response.status_code == 401
            body = response.json()
            assert body["detail"] is None
            assert "microsoftonline" not in str(body)
        finally:
            app.dependency_overrides.pop(get_auth_facade, None)

    def test_auth_failure_logged_at_warning(
        self, entra_client: TestClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        app.dependency_overrides[get_auth_facade] = _mock_facade_unauthorized
        try:
            with caplog.at_level(logging.WARNING, logger=AUTH_DEPS_LOGGER):
                entra_client.post(
                    "/v1/dummies",
                    json={"name": "X"},
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
            app.dependency_overrides.pop(get_auth_facade, None)


class TestForbiddenSanitization:
    def test_forbidden_does_not_reveal_role_name(
        self, entra_client: TestClient
    ) -> None:
        app.dependency_overrides[get_auth_facade] = _mock_facade_reader_principal
        try:
            response = entra_client.post(
                "/v2/dummies",
                json={"name": "X"},
                headers={"Authorization": "Bearer valid-token"},
            )
            assert response.status_code == 403
            body = response.json()
            assert body["errorCode"] == "FORBIDDEN"
            assert body["message"] == "Access forbidden"
            assert body["detail"] is None
            assert "admin" not in str(body).lower()
        finally:
            app.dependency_overrides.pop(get_auth_facade, None)

    def test_role_failure_logged_at_warning(
        self, entra_client: TestClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        app.dependency_overrides[get_auth_facade] = _mock_facade_reader_principal
        try:
            with caplog.at_level(logging.WARNING, logger=AUTH_DEPS_LOGGER):
                entra_client.post(
                    "/v2/dummies",
                    json={"name": "X"},
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
            app.dependency_overrides.pop(get_auth_facade, None)
