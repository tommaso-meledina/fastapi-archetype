from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.core.errors import AppException, ErrorCode
from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.contracts.dummy_service import DummyServiceContract

if TYPE_CHECKING:
    from sqlmodel import Session


class MockDummyService(DummyServiceContract):
    def __init__(self) -> None:
        self._store: dict[str, Dummy] = {}

    def get_all_dummies(self, session: Session) -> list[Dummy]:
        _ = session
        return list(self._store.values())

    def get_dummy_by_uuid(self, session: Session, uuid: str) -> Dummy | None:
        _ = session
        return self._store.get(uuid)

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        _ = session
        self._store[dummy.uuid] = dummy
        return dummy

    def update_dummy(self, session: Session, entity: Dummy) -> Dummy:
        _ = session
        if entity.uuid not in self._store:
            raise AppException(
                ErrorCode.DUMMY_NOT_FOUND,
                detail="Dummy not found",
            )
        updated = Dummy(
            id=entity.id or self._store[entity.uuid].id,
            uuid=entity.uuid,
            name=entity.name,
            description=entity.description,
        )
        self._store[entity.uuid] = updated
        return updated
