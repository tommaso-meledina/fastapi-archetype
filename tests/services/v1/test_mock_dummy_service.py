from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v1.implementations.mock_dummy_service import (
    MockDummyService,
)

if TYPE_CHECKING:
    from sqlmodel import Session


def test_mock_get_all_empty(session: Session) -> None:
    svc = MockDummyService()
    assert svc.get_all_dummies(session) == []


def test_mock_create_and_get_all(session: Session) -> None:
    svc = MockDummyService()
    dummy = Dummy(name="A", description="a")
    created = svc.create_dummy(session, dummy)
    assert created.uuid == dummy.uuid
    all_ = svc.get_all_dummies(session)
    assert len(all_) == 1
    assert all_[0].name == "A"


def test_mock_get_by_uuid(session: Session) -> None:
    svc = MockDummyService()
    dummy = Dummy(name="B", description="b")
    svc.create_dummy(session, dummy)
    found = svc.get_dummy_by_uuid(session, dummy.uuid)
    assert found is not None
    assert found.name == "B"
    unknown = "00000000-0000-0000-0000-000000000000"
    assert svc.get_dummy_by_uuid(session, unknown) is None


def test_mock_update(session: Session) -> None:
    svc = MockDummyService()
    dummy = Dummy(name="C", description="c")
    svc.create_dummy(session, dummy)
    updated_entity = Dummy(uuid=dummy.uuid, name="C2", description="c2")
    updated = svc.update_dummy(session, updated_entity)
    assert updated.name == "C2"
    assert updated.description == "c2"
    all_ = svc.get_all_dummies(session)
    assert len(all_) == 1
    assert all_[0].name == "C2"
