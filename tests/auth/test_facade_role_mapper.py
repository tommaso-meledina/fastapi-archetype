from unittest.mock import AsyncMock

from fastapi_archetype.auth.contracts import RoleMappingProvider
from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.auth.providers.role_mapping import BasicRoleMappingProvider
from fastapi_archetype.core.config import AppSettings


class GuidRoleMappingProvider(RoleMappingProvider):
    """Test provider that maps role names to GUIDs."""

    _mapping = {
        "admin": "guid-admin-001",
        "writer": "guid-writer-002",
        "reader": "guid-reader-003",
    }

    def to_external(self, role_name: str) -> str:
        return self._mapping.get(role_name, role_name)


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
