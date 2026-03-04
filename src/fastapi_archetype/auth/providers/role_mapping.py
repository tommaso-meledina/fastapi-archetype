from __future__ import annotations

from fastapi_archetype.auth.contracts import RoleMappingProvider


class BasicRoleMappingProvider(RoleMappingProvider):
    """Identity mapping — returns the role name unchanged."""

    def to_external(self, role_name: str) -> str:
        return role_name
