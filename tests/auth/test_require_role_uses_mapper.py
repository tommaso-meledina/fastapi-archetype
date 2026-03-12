from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.dependencies import get_auth_functions
from fastapi_archetype.auth.entra import (
    _decode_and_verify,
    _principal_from_claims,
    _select_signing_key,
    _validate_signing_key_metadata,
)
from fastapi_archetype.auth.models import AuthFunctions
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app

TEST_ISSUER = "https://test-issuer.example.com/"
TEST_AUDIENCE = "api://test-audience"
TEST_KID = "test-key-1"


def _guid_role_mapper(role: str) -> str:
    mapping = {
        "admin": "guid-admin-001",
        "writer": "guid-writer-002",
        "reader": "guid-reader-003",
    }
    return mapping.get(role, role)


def _build_guid_mapped_auth_functions(
    jwks_response: dict[str, Any],
) -> AuthFunctions:
    settings = AppSettings(
        auth_type="entra",
        auth_external_issuer=TEST_ISSUER,
        auth_external_audience=TEST_AUDIENCE,
        auth_external_jwks_uri="https://test-issuer.example.com/keys",
        auth_external_token_uri="https://test-issuer.example.com/token",
        auth_external_client_id="test-client-id",
        auth_external_client_secret="test-secret",
    )

    async def authenticate_bearer_token(token: str) -> Any:
        import jwt as _jwt

        try:
            header = _jwt.get_unverified_header(token)
        except _jwt.InvalidTokenError as exc:
            from fastapi_archetype.auth.contracts import UnauthorizedError

            raise UnauthorizedError("Malformed bearer token") from exc

        alg = header.get("alg")
        if not isinstance(alg, str):
            from fastapi_archetype.auth.contracts import UnauthorizedError

            raise UnauthorizedError("Missing token algorithm")

        signing_key = _select_signing_key(jwks_response, header.get("kid"))
        _validate_signing_key_metadata(signing_key, alg)
        claims = _decode_and_verify(token, signing_key, alg)

        from fastapi_archetype.auth.contracts import UnauthorizedError

        iss = claims.get("iss")
        if settings.auth_external_issuer and iss != settings.auth_external_issuer:
            raise UnauthorizedError("Invalid token issuer")
        required_audience = settings.auth_external_audience
        if required_audience:
            aud = claims.get("aud")
            aud_match = (isinstance(aud, str) and aud == required_audience) or (
                isinstance(aud, list) and required_audience in aud
            )
            if not aud_match:
                raise UnauthorizedError("Invalid token audience")

        return _principal_from_claims(claims)

    from unittest.mock import AsyncMock

    return AuthFunctions(
        authenticate_bearer_token=authenticate_bearer_token,
        get_client_credentials_access_token=AsyncMock(return_value="fake-token"),
        get_on_behalf_of_access_token=AsyncMock(return_value="fake-obo-token"),
        role_mapper=_guid_role_mapper,
    )


class TestRequireRoleUsesMapper:
    """Verify that require_role goes through role_mapper for the comparison."""

    @pytest.fixture(name="_guid_engine", scope="module")
    def guid_engine_fixture(self):
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

    @pytest.fixture(name="guid_client")
    def guid_client_fixture(
        self, _guid_engine, sign_jwt, jwks_response
    ) -> Generator[TestClient]:
        """Client using a GUID role mapper where 'admin' -> 'guid-admin-001'."""
        auth_fns = _build_guid_mapped_auth_functions(jwks_response)

        def _override_session():
            with Session(_guid_engine) as session:
                yield session

        def _override_auth_fns() -> AuthFunctions:
            return auth_fns

        app.dependency_overrides[get_session] = _override_session
        app.dependency_overrides[get_auth_functions] = _override_auth_fns
        limiter.reset()

        with (
            patch("fastapi_archetype.auth.dependencies.settings.auth_type", "entra"),
            TestClient(app) as c,
        ):
            yield c

        app.dependency_overrides.clear()

    def test_guid_mapped_role_grants_access(
        self,
        guid_client: TestClient,
        sign_jwt,
    ) -> None:
        token = sign_jwt({"roles": ["guid-admin-001"]})
        response = guid_client.post(
            "/test/admin-required",
            json={"value": "GuidAdmin"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    def test_unmapped_admin_string_denied_with_guid_mapper(
        self,
        guid_client: TestClient,
        sign_jwt,
    ) -> None:
        token = sign_jwt({"roles": ["admin"]})
        response = guid_client.post(
            "/test/admin-required",
            json={"value": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
