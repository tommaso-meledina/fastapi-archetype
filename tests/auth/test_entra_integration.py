"""Synthetic IdP integration tests for the Entra auth provider.

These tests exercise the full bearer-token validation path using a test-generated
RSA keypair. The provider's HTTP methods are monkeypatched to return matching JWKS
and mock responses so no external infrastructure is needed.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.dependencies import get_auth_facade
from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.providers.entra import EntraExternalAuthProvider
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app

TEST_ISSUER = "https://test-issuer.example.com/"
TEST_AUDIENCE = "api://test-audience"
TEST_KID = "test-key-1"

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


def _entra_settings(**overrides: Any) -> AppSettings:
    defaults = {
        "auth_type": "entra",
        "auth_external_issuer": TEST_ISSUER,
        "auth_external_audience": TEST_AUDIENCE,
        "auth_external_jwks_uri": "https://test-issuer.example.com/keys",
        "auth_external_token_uri": "https://test-issuer.example.com/token",
        "auth_external_client_id": "test-client-id",
        "auth_external_client_secret": "test-secret",
    }
    defaults.update(overrides)
    # Test fixture: dict overlay; Pydantic validates at runtime.
    return AppSettings(**defaults)  # type: ignore[call-arg]


def _build_patched_provider(
    jwks_response: dict[str, Any],
) -> EntraExternalAuthProvider:
    settings = _entra_settings()
    provider = EntraExternalAuthProvider(settings)

    async def _fake_http_get(
        url: str, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        _ = headers
        if "keys" in url or "jwks" in url:
            return jwks_response
        return {}

    async def _fake_http_post_form(_url: str, _data: dict[str, str]) -> dict[str, Any]:
        return {"access_token": "fake-obo-token"}

    provider._http_get = _fake_http_get  # type: ignore[method-assign]
    provider._http_post_form = _fake_http_post_form  # type: ignore[method-assign]
    return provider


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


@pytest.fixture(name="entra_integration_client")
def entra_integration_client_fixture(
    _entra_engine,
    jwks_response: dict[str, Any],
) -> Generator[TestClient]:
    provider = _build_patched_provider(jwks_response)
    facade = AuthFacade(primary_provider=provider)

    def _override_session():
        with Session(_entra_engine) as session:
            yield session

    def _override_facade() -> AuthFacade:
        return facade

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_auth_facade] = _override_facade
    limiter.reset()

    with (
        patch("fastapi_archetype.auth.dependencies._settings.auth_type", "entra"),
        TestClient(app) as c,
    ):
        yield c

    app.dependency_overrides.clear()


class TestProviderLevelValidation:
    """Direct provider-level tests for full authenticate_bearer_token path."""

    @pytest.mark.anyio
    async def test_valid_token_returns_correct_principal(
        self,
        sign_jwt: Callable[..., str],
        jwks_response: dict[str, Any],
    ) -> None:
        provider = _build_patched_provider(jwks_response)
        token = sign_jwt()
        principal = await provider.authenticate_bearer_token(token)
        assert principal.subject == "test-subject"
        assert principal.user_id == "test-oid-123"
        assert principal.name == "Test User"
        assert "admin" in principal.roles
        assert "reader" in principal.roles
        assert principal.claims["iss"] == TEST_ISSUER
        assert principal.claims["aud"] == TEST_AUDIENCE

    @pytest.mark.anyio
    async def test_expired_token_raises(
        self,
        sign_jwt: Callable[..., str],
        jwks_response: dict[str, Any],
    ) -> None:
        provider = _build_patched_provider(jwks_response)
        token = sign_jwt({"exp": int(time.time()) - 600})
        with pytest.raises(Exception, match="expired"):
            await provider.authenticate_bearer_token(token)

    @pytest.mark.anyio
    async def test_wrong_issuer_raises(
        self,
        sign_jwt: Callable[..., str],
        jwks_response: dict[str, Any],
    ) -> None:
        provider = _build_patched_provider(jwks_response)
        token = sign_jwt({"iss": "https://wrong-issuer.example.com/"})
        with pytest.raises(Exception, match="issuer"):
            await provider.authenticate_bearer_token(token)

    @pytest.mark.anyio
    async def test_wrong_audience_raises(
        self,
        sign_jwt: Callable[..., str],
        jwks_response: dict[str, Any],
    ) -> None:
        provider = _build_patched_provider(jwks_response)
        token = sign_jwt({"aud": "api://wrong-audience"})
        with pytest.raises(Exception, match="audience"):
            await provider.authenticate_bearer_token(token)

    @pytest.mark.anyio
    async def test_invalid_signature_raises(
        self,
        sign_jwt: Callable[..., str],
        jwks_response: dict[str, Any],
    ) -> None:
        wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        wrong_pem = wrong_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        provider = _build_patched_provider(jwks_response)
        token = sign_jwt(private_pem=wrong_pem)
        with pytest.raises(Exception, match="signature"):
            await provider.authenticate_bearer_token(token)

    @pytest.mark.anyio
    async def test_malformed_token_raises(
        self,
        jwks_response: dict[str, Any],
    ) -> None:
        provider = _build_patched_provider(jwks_response)
        with pytest.raises(Exception, match="[Mm]alformed"):
            await provider.authenticate_bearer_token("not-a-jwt")


class TestEndpointIntegration:
    """Full endpoint integration tests using TestClient with synthetic tokens."""

    def test_valid_token_grants_access_to_auth_protected_endpoint(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt()
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "AuthedItem"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["value"] == "AuthedItem"

    def test_valid_admin_token_grants_access_to_role_protected_endpoint(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"roles": ["admin"]})
        response = entra_integration_client.post(
            "/test/admin-required",
            json={"value": "AdminItem"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    def test_missing_token_returns_sanitized_401(
        self,
        entra_integration_client: TestClient,
    ) -> None:
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "X"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["errorCode"] == "UNAUTHORIZED"
        assert body["detail"] is None

    def test_expired_token_returns_sanitized_401(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"exp": int(time.time()) - 600})
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["errorCode"] == "UNAUTHORIZED"
        assert body["detail"] is None

    def test_wrong_issuer_returns_sanitized_401(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"iss": "https://evil.example.com/"})
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["detail"] is None

    def test_wrong_audience_returns_sanitized_401(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"aud": "api://wrong"})
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["detail"] is None

    def test_invalid_signature_returns_sanitized_401(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        wrong_pem = wrong_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        token = sign_jwt(private_pem=wrong_pem)
        response = entra_integration_client.post(
            "/test/auth-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        body = response.json()
        assert body["detail"] is None


class TestRoleEnforcement:
    """Role enforcement tests using synthetic tokens."""

    def test_reader_only_gets_403_on_admin_endpoint(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"roles": ["reader"]})
        response = entra_integration_client.post(
            "/test/admin-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        body = response.json()
        assert body["errorCode"] == "FORBIDDEN"
        assert body["detail"] is None

    def test_admin_role_grants_access(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"roles": ["admin"]})
        response = entra_integration_client.post(
            "/test/admin-required",
            json={"value": "AdminWidget"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    def test_missing_roles_claim_denied_fail_closed(
        self,
        entra_integration_client: TestClient,
        sign_jwt: Callable[..., str],
    ) -> None:
        token = sign_jwt({"roles": None})
        response = entra_integration_client.post(
            "/test/admin-required",
            json={"value": "NoRoles"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
