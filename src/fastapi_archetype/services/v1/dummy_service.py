from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics

if TYPE_CHECKING:
    from sqlmodel import Session


def get_all_dummies(session: Session) -> list[Dummy]:
    return list(session.exec(select(Dummy)).all())


def create_dummy(session: Session, dummy: Dummy) -> Dummy:
    session.add(dummy)
    session.commit()
    session.refresh(dummy)
    metrics.counters.dummies_created_total.labels(api_version="v1").inc()
    return dummy
