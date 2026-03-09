"""Mock v1 dummy service returning static values only (no in-memory state)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.core.errors import AppException, ErrorCode
from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.contracts.dummy_service import DummyServiceContract

if TYPE_CHECKING:
    from sqlmodel import Session

# Static mock data — no logic, no state.
MOCK_UUID_1 = "00000000-0000-0000-0000-000000000001"
MOCK_UUID_CREATED = "00000000-0000-0000-0000-000000000002"
MOCK_UUID_UPDATED = "00000000-0000-0000-0000-000000000003"

STATIC_LIST: list[Dummy] = [
    Dummy(id=1, uuid=MOCK_UUID_1, name="Static Mock One", description="v1 mock"),
]
STATIC_GET_BY_UUID: Dummy | None = Dummy(
    id=1, uuid=MOCK_UUID_1, name="Static Mock One", description="v1 mock"
)
STATIC_CREATED = Dummy(
    id=2, uuid=MOCK_UUID_CREATED, name="Mock Created", description="static"
)
STATIC_UPDATED = Dummy(
    id=1, uuid=MOCK_UUID_UPDATED, name="Mock Updated", description="static"
)


class MockDummyService(DummyServiceContract):
    """Returns static mock data only. No persistence or logic."""

    def get_all_dummies(self, session: Session) -> list[Dummy]:
        _ = session
        return list(STATIC_LIST)

    def get_dummy_by_uuid(self, session: Session, uuid: str) -> Dummy | None:
        _ = session
        if uuid == MOCK_UUID_1:
            return STATIC_GET_BY_UUID
        return None

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        _ = session
        _ = dummy
        return STATIC_CREATED

    def update_dummy(self, session: Session, entity: Dummy) -> Dummy:
        _ = session
        if entity.uuid != MOCK_UUID_1 and entity.uuid != MOCK_UUID_CREATED:
            raise AppException(
                ErrorCode.DUMMY_NOT_FOUND,
                detail="Dummy not found",
            )
        return STATIC_UPDATED
