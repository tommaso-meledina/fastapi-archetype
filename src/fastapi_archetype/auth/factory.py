from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.providers import (
    EntraExternalAuthProvider,
    NoAuthProvider,
)

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings


def build_auth_facade(settings: AppSettings) -> AuthFacade:
    if settings.auth_type == "none":
        return AuthFacade(primary_provider=NoAuthProvider())
    return AuthFacade(primary_provider=EntraExternalAuthProvider(settings))
