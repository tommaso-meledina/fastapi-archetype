from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v1.implementations.default_dummy_service import (
    DefaultDummyServiceV1,
)

if TYPE_CHECKING:
    from sqlmodel import Session


def test_get_all_dummies_empty(session: Session) -> None:
    svc = DefaultDummyServiceV1()
    result = svc.get_all_dummies(session)
    assert result == []


def test_get_all_dummies_returns_all(session: Session) -> None:
    session.add(Dummy(name="A"))
    session.add(Dummy(name="B"))
    session.commit()

    svc = DefaultDummyServiceV1()
    result = svc.get_all_dummies(session)
    assert len(result) == 2
    names = {d.name for d in result}
    assert names == {"A", "B"}


def test_create_dummy_persists(session: Session) -> None:
    dummy = Dummy(name="Created", description="desc")
    svc = DefaultDummyServiceV1()
    result = svc.create_dummy(session, dummy)
    assert result.id is not None
    assert result.uuid is not None
    assert result.name == "Created"
    assert result.description == "desc"


def test_create_dummy_assigns_id(session: Session) -> None:
    dummy = Dummy(name="AutoID")
    svc = DefaultDummyServiceV1()
    result = svc.create_dummy(session, dummy)
    assert isinstance(result.id, int)
    assert result.id > 0
    assert isinstance(result.uuid, str)
    assert len(result.uuid) > 0
