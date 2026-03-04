from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from fastapi_archetype.core.constants import DUMMIES
from fastapi_archetype.core.database import get_session
from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.services import dummy_service

if TYPE_CHECKING:
    from sqlmodel import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix=DUMMIES.path, tags=[f"{DUMMIES.name} v2"])


@router.get("", response_model=list[Dummy])
def list_dummies(session: Session = Depends(get_session)) -> list[Dummy]:
    results = dummy_service.get_all_dummies(session)
    logger.info("v2 list_dummies returned %d item(s)", len(results))
    return results


@router.post("", response_model=Dummy, status_code=status.HTTP_201_CREATED)
def create_dummy(dummy: Dummy, session: Session = Depends(get_session)) -> Dummy:
    created = dummy_service.create_dummy(session, dummy)
    logger.info("v2 create_dummy id=%s name=%r", created.id, created.name)
    return created
