from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from fastapi_archetype.core.constants import DUMMIES
from fastapi_archetype.core.database import get_session
from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.services import dummy_service

if TYPE_CHECKING:
    from sqlmodel import Session

router = APIRouter(prefix=DUMMIES.path, tags=[DUMMIES.name])


@router.get("", response_model=list[Dummy])
def list_dummies(session: Session = Depends(get_session)) -> list[Dummy]:
    return dummy_service.get_all_dummies(session)


@router.post("", response_model=Dummy, status_code=status.HTTP_201_CREATED)
def create_dummy(dummy: Dummy, session: Session = Depends(get_session)) -> Dummy:
    return dummy_service.create_dummy(session, dummy)
