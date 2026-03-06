from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_archetype.auth.contracts import UnauthorizedError
from fastapi_archetype.auth.facade import AuthFacade  # noqa: TC001
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.auth.models import Principal, Role  # noqa: TC001
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.errors import AppException, ErrorCode

logger = logging.getLogger(__name__)

_settings = AppSettings()
bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_auth_facade() -> AuthFacade:
    return build_auth_facade(AppSettings())


async def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str | None:
    if credentials is None:
        return None
    return credentials.credentials


async def get_current_principal(
    token: Annotated[str | None, Depends(get_bearer_token)],
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> Principal:
    if _settings.auth_type == "none":
        principal = await facade.authenticate_bearer_token(token or "")
        return principal
    if token is None:
        raise AppException(ErrorCode.UNAUTHORIZED)
    try:
        principal = await facade.authenticate_bearer_token(token)
    except UnauthorizedError as exc:
        logger.warning("Bearer token authentication failed: %s", exc)
        raise AppException(ErrorCode.UNAUTHORIZED) from exc
    except AppException:
        raise
    except Exception as exc:
        logger.warning("Unexpected authentication error: %s", exc)
        raise AppException(ErrorCode.UNAUTHORIZED) from exc
    return principal


async def require_auth(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> Principal:
    return principal


def require_role(required_role: Role):
    async def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
        auth_facade: Annotated[AuthFacade, Depends(get_auth_facade)],
    ) -> Principal:
        roles = {role.lower() for role in principal.roles}
        external_role = auth_facade.role_mapper.to_external(required_role.value).lower()
        if external_role not in roles:
            logger.warning(
                "Role check failed: principal %s lacks role %s (they have %d roles)",
                principal.subject,
                required_role.value,
                len(roles),
            )
            raise AppException(ErrorCode.FORBIDDEN)
        return principal

    return _dependency
