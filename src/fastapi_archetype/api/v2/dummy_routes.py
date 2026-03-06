from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Request, Response, status

from fastapi_archetype.auth.dependencies import require_role
from fastapi_archetype.auth.models import Role
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.constants import DUMMIES
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.services.v2 import dummy_service

if TYPE_CHECKING:
    from sqlmodel import Session

    from fastapi_archetype.auth.models import Principal

router = APIRouter(prefix=DUMMIES.path, tags=[f"{DUMMIES.name} v2"])
_settings = AppSettings()


@router.get("", response_model=list[Dummy])
@limiter.limit(_settings.rate_limit_get_dummies)
def list_dummies(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> list[Dummy]:
    return dummy_service.get_all_dummies(session)


@router.post("", response_model=Dummy, status_code=status.HTTP_201_CREATED)
@limiter.limit(_settings.rate_limit_post_dummies)
def create_dummy(
    request: Request,
    dummy: Dummy,
    response: Response,
    principal: Principal = Depends(require_role(Role.ADMIN)),
    session: Session = Depends(get_session),
) -> Dummy:
    _ = principal
    return dummy_service.create_dummy(session, dummy)
