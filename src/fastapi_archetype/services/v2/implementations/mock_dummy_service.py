"""Mock v2 dummy service returning static values only (no in-memory state)."""

from sqlmodel import Session

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV2Contract

# Static mock data — no logic, no state.
MOCK_V2_UUID_1 = "00000000-0000-0000-0000-000000000010"
MOCK_V2_CREATED_UUID = "00000000-0000-0000-0000-000000000011"

STATIC_LIST_V2: list[Dummy] = [
    Dummy(id=10, uuid=MOCK_V2_UUID_1, name="Static Mock V2", description="v2 mock"),
]
STATIC_CREATED_V2 = Dummy(
    id=11, uuid=MOCK_V2_CREATED_UUID, name="Mock Created V2", description="static"
)


class MockDummyServiceV2(DummyServiceV2Contract):
    """Returns static mock data only. No persistence or logic."""

    def get_all_dummies(self, session: Session) -> list[Dummy]:
        _ = session
        return list(STATIC_LIST_V2)

    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy:
        _ = session
        _ = dummy
        return STATIC_CREATED_V2
