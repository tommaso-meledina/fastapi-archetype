from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_archetype.models.dummy import Dummy

if TYPE_CHECKING:
    from sqlmodel import Session


def get_all_dummies(session: Session) -> list[Dummy]:
    return list(session.exec(select(Dummy)).all())


def create_dummy(session: Session, dummy: Dummy) -> Dummy:
    session.add(dummy)
    session.commit()
    session.refresh(dummy)
    return dummy
