from collections.abc import Generator
from typing import Any, cast
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.contracts import RoleMappingProvider
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


class GuidRoleMappingProvider(RoleMappingProvider):
    """Test provider that maps role names to GUIDs."""

    _mapping = {
        "admin": "guid-admin-001",
        "writer": "guid-writer-002",
        "reader": "guid-reader-003",
    }

    def to_external(self, role_name: str) -> str:
        return self._mapping.get(role_name, role_name)


class TestRequireRoleUsesMapper:
    """Verify that require_role goes through to_external for the comparison."""

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
        """Client using GuidRoleMappingProvider where 'admin' -> 'guid-admin-001'."""
        settings = AppSettings(
            auth_type="entra",
            auth_external_issuer=TEST_ISSUER,
            auth_external_audience=TEST_AUDIENCE,
            auth_external_jwks_uri="https://test-issuer.example.com/keys",
            auth_external_token_uri="https://test-issuer.example.com/token",
            auth_external_client_id="test-client-id",
            auth_external_client_secret="test-secret",
        )
        provider = EntraExternalAuthProvider(settings)

        async def _fake_http_get(
            _url: str, _headers: dict[str, str] | None = None
        ) -> dict[str, Any]:
            return jwks_response

        async def _fake_http_post_form(
            _url: str, _data: dict[str, str]
        ) -> dict[str, Any]:
            return {"access_token": "fake-token"}

        cast(Any, provider)._http_get = _fake_http_get
        cast(Any, provider)._http_post_form = _fake_http_post_form

        guid_mapper = GuidRoleMappingProvider()
        facade = AuthFacade(primary_provider=provider, role_mapper=guid_mapper)

        def _override_session():
            with Session(_guid_engine) as session:
                yield session

        def _override_facade() -> AuthFacade:
            return facade

        app.dependency_overrides[get_session] = _override_session
        app.dependency_overrides[get_auth_facade] = _override_facade
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
