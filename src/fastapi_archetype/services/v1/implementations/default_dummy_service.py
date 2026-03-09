from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_archetype.core.errors import AppException, ErrorCode
from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics
from fastapi_archetype.services.contracts.dummy_service import DummyServiceContract

if TYPE_CHECKING:
    from sqlmodel import Session


class DefaultDummyService(DummyServiceContract):
    def get_all_dummies(self, session: Session) -> list[Dummy]:
        return list(session.exec(select(Dummy)).all())

    def get_dummy_by_uuid(self, session: Session, uuid: str) -> Dummy | None:
        return session.exec(select(Dummy).where(Dummy.uuid == uuid)).first()

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        session.add(dummy)
        session.commit()
        session.refresh(dummy)
        metrics.counters.dummies_created_total.labels(api_version="v1").inc()
        return dummy

    def update_dummy(self, session: Session, entity: Dummy) -> Dummy:
        if entity.id is None:
            existing = self.get_dummy_by_uuid(session, entity.uuid)
            if existing is None:
                raise AppException(
                    ErrorCode.DUMMY_NOT_FOUND,
                    detail="Dummy not found",
                )
            entity = Dummy(
                id=existing.id,
                uuid=existing.uuid,
                name=entity.name,
                description=entity.description,
            )
        merged = session.merge(entity)
        session.commit()
        session.refresh(merged)
        return merged
