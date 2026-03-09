from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v1.implementations.mock_dummy_service import (
    MOCK_UUID_1,
    MOCK_UUID_CREATED,
    STATIC_CREATED,
    STATIC_LIST,
    STATIC_UPDATED,
    MockDummyServiceV1,
)

if TYPE_CHECKING:
    from sqlmodel import Session


def test_mock_get_all_returns_static_list(session: Session) -> None:
    svc = MockDummyServiceV1()
    result = svc.get_all_dummies(session)
    assert result == STATIC_LIST
    assert len(result) == 1
    assert result[0].uuid == MOCK_UUID_1
    assert result[0].name == "Static Mock One"


def test_mock_create_returns_static(session: Session) -> None:
    svc = MockDummyServiceV1()
    created = svc.create_dummy(session, Dummy(name="Ignored", description="x"))
    assert created == STATIC_CREATED
    assert created.uuid == MOCK_UUID_CREATED
    assert created.name == "Mock Created"


def test_mock_get_by_uuid_returns_static_for_known(session: Session) -> None:
    svc = MockDummyServiceV1()
    found = svc.get_dummy_by_uuid(session, MOCK_UUID_1)
    assert found is not None
    assert found.uuid == MOCK_UUID_1
    assert found.name == "Static Mock One"


def test_mock_get_by_uuid_returns_none_for_unknown(session: Session) -> None:
    svc = MockDummyServiceV1()
    unknown = "00000000-0000-0000-0000-000000000099"
    assert svc.get_dummy_by_uuid(session, unknown) is None


def test_mock_update_returns_static_for_known_uuid(session: Session) -> None:
    svc = MockDummyServiceV1()
    entity = Dummy(uuid=MOCK_UUID_1, name="Any", description="any")
    updated = svc.update_dummy(session, entity)
    assert updated == STATIC_UPDATED
    assert updated.name == "Mock Updated"


def test_mock_update_raises_for_unknown_uuid(session: Session) -> None:
    import pytest

    from fastapi_archetype.core.errors import AppException, ErrorCode

    svc = MockDummyServiceV1()
    unknown_uuid = "00000000-0000-0000-0000-000000000099"
    entity = Dummy(uuid=unknown_uuid, name="X", description="x")
    with pytest.raises(AppException) as exc_info:
        svc.update_dummy(session, entity)
    assert exc_info.value.error_code == ErrorCode.DUMMY_NOT_FOUND
