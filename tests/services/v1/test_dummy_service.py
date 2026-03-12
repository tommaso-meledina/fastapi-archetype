from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.services.v1 import dummy as v1_dummy


async def test_get_all_dummies_empty(session: AsyncSession) -> None:
    result = await v1_dummy.get_all_dummies(session)
    assert result == []


async def test_get_all_dummies_returns_all(session: AsyncSession) -> None:
    session.add(Dummy(name="A"))
    session.add(Dummy(name="B"))
    await session.commit()

    result = await v1_dummy.get_all_dummies(session)
    assert len(result) == 2
    names = {d.name for d in result}
    assert names == {"A", "B"}


async def test_create_dummy_persists(session: AsyncSession) -> None:
    dummy = Dummy(name="Created", description="desc")
    result = await v1_dummy.create_dummy(session, dummy)
    assert result.id is not None
    assert result.uuid is not None
    assert result.name == "Created"
    assert result.description == "desc"


async def test_create_dummy_assigns_id(session: AsyncSession) -> None:
    dummy = Dummy(name="AutoID")
    result = await v1_dummy.create_dummy(session, dummy)
    assert isinstance(result.id, int)
    assert result.id > 0
    assert isinstance(result.uuid, str)
    assert len(result.uuid) > 0
