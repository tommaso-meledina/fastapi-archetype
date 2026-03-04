from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
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
    request: Request,
    token: Annotated[str | None, Depends(get_bearer_token)],
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> Principal:
    if _settings.auth_type == "none":
        principal = await facade.authenticate_bearer_token(token or "")
        request.state.current_principal = principal
        request.state.bearer_token = ""
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
    request.state.current_principal = principal
    request.state.bearer_token = token
    return principal


async def require_auth(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> Principal:
    return principal


def require_role(required_role: Role):
    async def _dependency(
        request: Request,
        principal: Annotated[Principal, Depends(get_current_principal)],
        facade: Annotated[AuthFacade, Depends(get_auth_facade)],
    ) -> Principal:
        roles = {role.lower() for role in principal.roles}
        if _settings.auth_type != "none" and _settings.auth_enforce_graph_roles:
            bearer_token = getattr(request.state, "bearer_token", None)
            if isinstance(bearer_token, str):
                try:
                    graph_roles = await facade.get_current_user_roles(
                        principal,
                        bearer_token,
                    )
                except Exception as exc:
                    logger.warning("Graph role enrichment failed: %s", exc)
                    raise AppException(ErrorCode.UNAUTHORIZED) from exc
                roles.update({role.lower() for role in graph_roles})
        if required_role.value not in roles:
            logger.warning(
                "Role check failed: principal %s lacks role %s",
                principal.subject,
                required_role.value,
            )
            raise AppException(ErrorCode.FORBIDDEN)
        return principal

    return _dependency
