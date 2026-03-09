from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV2Contract

if TYPE_CHECKING:
    from sqlmodel import Session

logger = logging.getLogger(__name__)


class DefaultDummyServiceV2(DummyServiceV2Contract):
    def get_all_dummies(self, session: Session) -> list[Dummy]:
        results = list(session.exec(select(Dummy)).all())
        logger.info("v2 get_all_dummies returned %d item(s)", len(results))
        return results

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        session.add(dummy)
        session.commit()
        session.refresh(dummy)
        metrics.counters.dummies_created_total.labels(api_version="v2").inc()
        logger.info("v2 create_dummy id=%s name=%r", dummy.id, dummy.name)
        return dummy
