from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.contracts import RoleMappingProvider
from fastapi_archetype.auth.dependencies import get_auth_facade
from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.auth.providers.role_mapping import BasicRoleMappingProvider
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app

if TYPE_CHECKING:
    from collections.abc import Generator

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


class TestBasicRoleMappingProvider:
    def test_to_external_returns_admin_unchanged(self) -> None:
        provider = BasicRoleMappingProvider()
        assert provider.to_external("admin") == "admin"

    def test_to_external_returns_reader_unchanged(self) -> None:
        provider = BasicRoleMappingProvider()
        assert provider.to_external("reader") == "reader"

    def test_to_external_returns_writer_unchanged(self) -> None:
        provider = BasicRoleMappingProvider()
        assert provider.to_external("writer") == "writer"

    def test_to_external_returns_arbitrary_string_unchanged(self) -> None:
        provider = BasicRoleMappingProvider()
        assert provider.to_external("custom-role") == "custom-role"


class TestRoleMappingProviderABC:
    def test_abc_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            RoleMappingProvider()  # type: ignore[abstract]

    def test_custom_provider_implements_contract(self) -> None:
        provider = GuidRoleMappingProvider()
        assert provider.to_external("admin") == "guid-admin-001"
        assert provider.to_external("reader") == "guid-reader-003"
        assert provider.to_external("unknown") == "unknown"


class TestFacadeRoleMapperProperty:
    def test_facade_exposes_role_mapper(self) -> None:
        facade = build_auth_facade(AppSettings(auth_type="none"))
        assert isinstance(facade.role_mapper, BasicRoleMappingProvider)

    def test_facade_accepts_custom_role_mapper(self) -> None:
        custom_mapper = GuidRoleMappingProvider()
        facade = AuthFacade(
            primary_provider=AsyncMock(),
            role_mapper=custom_mapper,
        )
        assert facade.role_mapper is custom_mapper

    def test_facade_defaults_to_basic_when_none(self) -> None:
        facade = AuthFacade(primary_provider=AsyncMock())
        assert isinstance(facade.role_mapper, BasicRoleMappingProvider)


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
        """Client using GuidRoleMappingProvider where 'admin' → 'guid-admin-001'."""
        from fastapi_archetype.auth.providers.entra import EntraExternalAuthProvider

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
            url: str, headers: dict[str, str] | None = None
        ) -> dict[str, Any]:
            return jwks_response

        async def _fake_http_post_form(
            url: str, data: dict[str, str]
        ) -> dict[str, Any]:
            return {"access_token": "fake-token"}

        provider._http_get = _fake_http_get  # type: ignore[method-assign]
        provider._http_post_form = _fake_http_post_form  # type: ignore[method-assign]

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
            patch("fastapi_archetype.auth.dependencies._settings.auth_type", "entra"),
            patch(
                "fastapi_archetype.auth.dependencies._settings.auth_enforce_graph_roles",
                False,
            ),
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
            "/v2/dummies",
            json={"name": "GuidAdmin"},
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
            "/v2/dummies",
            json={"name": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
