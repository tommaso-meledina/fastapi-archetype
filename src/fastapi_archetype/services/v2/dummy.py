import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics

logger = logging.getLogger(__name__)


async def get_all_dummies(session: AsyncSession) -> list[Dummy]:
    result = await session.execute(select(Dummy))
    results = list(result.scalars().all())
    logger.info("v2 get_all_dummies returned %d item(s)", len(results))
    return results


async def create_dummy(session: AsyncSession, dummy: Dummy) -> Dummy:
    session.add(dummy)
    await session.commit()
    await session.refresh(dummy)
    metrics.counters.dummies_created_total.labels(api_version="v2").inc()
    logger.info("v2 create_dummy id=%s name=%r", dummy.id, dummy.name)
    return dummy
