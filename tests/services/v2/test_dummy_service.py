import logging

from pytest import LogCaptureFixture
from sqlmodel import Session

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v2 import dummy as v2_dummy

V2_LOGGER = "fastapi_archetype.services.v2.dummy"


def test_get_all_dummies_empty(session: Session) -> None:
    result = v2_dummy.get_all_dummies(session)
    assert result == []


def test_get_all_dummies_returns_all(session: Session) -> None:
    session.add(Dummy(name="A"))
    session.add(Dummy(name="B"))
    session.commit()

    result = v2_dummy.get_all_dummies(session)
    assert len(result) == 2
    names = {d.name for d in result}
    assert names == {"A", "B"}


def test_create_dummy_persists(session: Session) -> None:
    dummy = Dummy(name="Created", description="desc")
    result = v2_dummy.create_dummy(session, dummy)
    assert result.id is not None
    assert result.name == "Created"
    assert result.description == "desc"


def test_get_all_dummies_logs(session: Session, caplog: LogCaptureFixture) -> None:
    session.add(Dummy(name="Logged"))
    session.commit()
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        v2_dummy.get_all_dummies(session)
    assert any("v2 get_all_dummies returned" in r.message for r in caplog.records)


def test_create_dummy_logs(session: Session, caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        v2_dummy.create_dummy(session, Dummy(name="LogMe"))
    assert any("v2 create_dummy" in r.message for r in caplog.records)
