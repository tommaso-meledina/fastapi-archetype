from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v2.implementations.mock_dummy_service import (
    MockDummyServiceV2,
)

if TYPE_CHECKING:
    from sqlmodel import Session


def test_mock_v2_get_all_empty(session: Session) -> None:
    svc = MockDummyServiceV2()
    assert svc.get_all_dummies(session) == []


def test_mock_v2_create_and_get_all(session: Session) -> None:
    svc = MockDummyServiceV2()
    dummy = Dummy(name="A", description="a")
    created = svc.create_dummy(session, dummy)
    assert created.uuid == dummy.uuid
    all_ = svc.get_all_dummies(session)
    assert len(all_) == 1
    assert all_[0].name == "A"
