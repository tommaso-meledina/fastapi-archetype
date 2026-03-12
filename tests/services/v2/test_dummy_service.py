import logging

from pytest import LogCaptureFixture
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v2 import dummy as v2_dummy

V2_LOGGER = "fastapi_archetype.services.v2.dummy"


async def test_get_all_dummies_empty(session: AsyncSession) -> None:
    result = await v2_dummy.get_all_dummies(session)
    assert result == []


async def test_get_all_dummies_returns_all(session: AsyncSession) -> None:
    session.add(Dummy(name="A"))
    session.add(Dummy(name="B"))
    await session.commit()

    result = await v2_dummy.get_all_dummies(session)
    assert len(result) == 2
    names = {d.name for d in result}
    assert names == {"A", "B"}


async def test_create_dummy_persists(session: AsyncSession) -> None:
    dummy = Dummy(name="Created", description="desc")
    result = await v2_dummy.create_dummy(session, dummy)
    assert result.id is not None
    assert result.name == "Created"
    assert result.description == "desc"


async def test_get_all_dummies_logs(
    session: AsyncSession, caplog: LogCaptureFixture
) -> None:
    session.add(Dummy(name="Logged"))
    await session.commit()
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        await v2_dummy.get_all_dummies(session)
    assert any("v2 get_all_dummies returned" in r.message for r in caplog.records)


async def test_create_dummy_logs(
    session: AsyncSession, caplog: LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=V2_LOGGER):
        await v2_dummy.create_dummy(session, Dummy(name="LogMe"))
    assert any("v2 create_dummy" in r.message for r in caplog.records)
