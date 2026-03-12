import logging

from pytest import LogCaptureFixture
from sqlmodel import Session

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v2.implementations.default_dummy_service import (
    DefaultDummyServiceV2,
)

V2_LOGGER = "fastapi_archetype.services.v2.implementations.default_dummy_service"


def test_get_all_dummies_empty(session: Session) -> None:
    svc = DefaultDummyServiceV2()
    result = svc.get_all_dummies(session)
    assert result == []


def test_get_all_dummies_returns_all(session: Session) -> None:
    session.add(Dummy(name="A"))
    session.add(Dummy(name="B"))
    session.commit()

    svc = DefaultDummyServiceV2()
    result = svc.get_all_dummies(session)
    assert len(result) == 2
    names = {d.name for d in result}
    assert names == {"A", "B"}


def test_create_dummy_persists(session: Session) -> None:
    dummy = Dummy(name="Created", description="desc")
    svc = DefaultDummyServiceV2()
    result = svc.create_dummy(session, dummy)
    assert result.id is not None
    assert result.name == "Created"
    assert result.description == "desc"


def test_get_all_dummies_logs(session: Session, caplog: LogCaptureFixture) -> None:
    session.add(Dummy(name="Logged"))
    session.commit()
    svc = DefaultDummyServiceV2()
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        svc.get_all_dummies(session)
    assert any("v2 get_all_dummies returned" in r.message for r in caplog.records)


def test_create_dummy_logs(session: Session, caplog: LogCaptureFixture) -> None:
    svc = DefaultDummyServiceV2()
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        svc.create_dummy(session, Dummy(name="LogMe"))
    assert any("v2 create_dummy" in r.message for r in caplog.records)
