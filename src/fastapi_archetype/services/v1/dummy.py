from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi_archetype.core.errors import AppException, ErrorCode
from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics


async def get_all_dummies(session: AsyncSession) -> list[Dummy]:
    result = await session.execute(select(Dummy))
    return list(result.scalars().all())


async def get_dummy_by_uuid(session: AsyncSession, uuid: str) -> Dummy | None:
    result = await session.execute(select(Dummy).where(Dummy.uuid == uuid))
    return result.scalars().first()


async def create_dummy(session: AsyncSession, dummy: Dummy) -> Dummy:
    session.add(dummy)
    await session.commit()
    await session.refresh(dummy)
    metrics.counters.dummies_created_total.labels(api_version="v1").inc()
    return dummy


async def update_dummy(session: AsyncSession, entity: Dummy) -> Dummy:
    if entity.id is None:
        existing = await get_dummy_by_uuid(session, entity.uuid)
        if existing is None:
            raise AppException(
                ErrorCode.DUMMY_NOT_FOUND,
                detail="Dummy not found",
            )
        entity = Dummy(
            id=existing.id,
            uuid=existing.uuid,
            name=entity.name,
            description=entity.description,
        )
    merged = await session.merge(entity)
    await session.commit()
    await session.refresh(merged)
    return merged
