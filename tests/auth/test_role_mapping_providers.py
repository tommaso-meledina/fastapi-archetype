import pytest

from fastapi_archetype.auth.contracts import RoleMappingProvider
from fastapi_archetype.auth.providers.role_mapping import BasicRoleMappingProvider


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
            RoleMappingProvider()

    def test_custom_provider_implements_contract(self) -> None:
        provider = GuidRoleMappingProvider()
        assert provider.to_external("admin") == "guid-admin-001"
        assert provider.to_external("reader") == "guid-reader-003"
        assert provider.to_external("unknown") == "unknown"
