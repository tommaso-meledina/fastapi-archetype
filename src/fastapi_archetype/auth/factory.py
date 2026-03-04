from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.providers import (
    EntraExternalAuthProvider,
    NoAuthProvider,
)
from fastapi_archetype.auth.providers.role_mapping import BasicRoleMappingProvider

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings


def build_auth_facade(settings: AppSettings) -> AuthFacade:
    role_mapper = BasicRoleMappingProvider()
    if settings.auth_type == "none":
        return AuthFacade(primary_provider=NoAuthProvider(), role_mapper=role_mapper)
    return AuthFacade(
        primary_provider=EntraExternalAuthProvider(settings),
        role_mapper=role_mapper,
    )
