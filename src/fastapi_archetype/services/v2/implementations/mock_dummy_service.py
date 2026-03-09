from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.entities.dummy import Dummy  # noqa: TC001
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV2Contract

if TYPE_CHECKING:
    from sqlmodel import Session


class MockDummyServiceV2(DummyServiceV2Contract):
    def __init__(self) -> None:
        self._store: dict[str, Dummy] = {}

    def get_all_dummies(self, session: Session) -> list[Dummy]:
        _ = session
        return list(self._store.values())

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        _ = session
        self._store[dummy.uuid] = dummy
        return dummy
