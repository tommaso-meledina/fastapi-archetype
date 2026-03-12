"""Mock v2 dummy service returning static values only (no in-memory state)."""

from sqlmodel import Session

from fastapi_archetype.models.entities.dummy import Dummy

MOCK_V2_UUID_1 = "00000000-0000-0000-0000-000000000010"
MOCK_V2_CREATED_UUID = "00000000-0000-0000-0000-000000000011"

STATIC_LIST_V2: list[Dummy] = [
    Dummy(id=10, uuid=MOCK_V2_UUID_1, name="Static Mock V2", description="v2 mock"),
]
STATIC_CREATED_V2 = Dummy(
    id=11, uuid=MOCK_V2_CREATED_UUID, name="Mock Created V2", description="static"
)


def get_all_dummies(session: Session) -> list[Dummy]:
    _ = session
    return list(STATIC_LIST_V2)


def create_dummy(session: Session, dummy: Dummy) -> Dummy:
    _ = (session, dummy)
    return STATIC_CREATED_V2
