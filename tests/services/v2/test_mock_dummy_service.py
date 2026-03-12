from sqlmodel import Session

from fastapi_archetype.services.v2.implementations.mock_dummy_service import (
    MOCK_V2_UUID_1,
    STATIC_CREATED_V2,
    STATIC_LIST_V2,
    MockDummyServiceV2,
)


def test_mock_v2_get_all_returns_static_list(session: Session) -> None:
    svc = MockDummyServiceV2()
    result = svc.get_all_dummies(session)
    assert result == STATIC_LIST_V2
    assert len(result) == 1
    assert result[0].uuid == MOCK_V2_UUID_1
    assert result[0].name == "Static Mock V2"


def test_mock_v2_create_returns_static(session: Session) -> None:
    from fastapi_archetype.models.entities.dummy import Dummy

    svc = MockDummyServiceV2()
    created = svc.create_dummy(session, Dummy(name="Ignored", description="x"))
    assert created == STATIC_CREATED_V2
    assert created.name == "Mock Created V2"
