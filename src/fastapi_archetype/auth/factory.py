from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.providers.none import NoAuthProvider
from fastapi_archetype.auth.providers.role_mapping import BasicRoleMappingProvider

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings


def build_auth_facade(settings: AppSettings) -> AuthFacade:
    role_mapper = BasicRoleMappingProvider()
    if settings.auth_type == "none":
        return AuthFacade(primary_provider=NoAuthProvider(), role_mapper=role_mapper)
    try:
        from fastapi_archetype.auth.providers.entra import EntraExternalAuthProvider
    except ModuleNotFoundError as exc:
        if exc.name == "httpx":
            msg = (
                "AUTH_TYPE=entra requires httpx at runtime. "
                "Install runtime dependencies before starting the app."
            )
            raise RuntimeError(msg) from exc
        raise
    return AuthFacade(
        primary_provider=EntraExternalAuthProvider(settings),
        role_mapper=role_mapper,
    )
