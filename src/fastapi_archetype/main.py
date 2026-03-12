import uuid as uuid_module
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, select

from fastapi_archetype.api.v1 import router as v1_router
from fastapi_archetype.api.v2 import router as v2_router
from fastapi_archetype.core.config import settings
from fastapi_archetype.core.constants import HEALTH_PATH
from fastapi_archetype.core.database import (
    dispose_engine,
    get_engine,
    is_local_dev_mode,
)
from fastapi_archetype.core.errors import (
    AppException,
    app_exception_handler,
    rate_limit_exceeded_handler,
    validation_exception_handler,
)
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.models.entities.dummy import Dummy
from fastapi_archetype.observability.logging import configure_logging
from fastapi_archetype.observability.otel import setup_otel
from fastapi_archetype.observability.prometheus import setup_prometheus


async def _backfill_dummy_uuids(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        result = await conn.execute(select(Dummy))
        rows = result.all()
        for row in rows:
            if not row.uuid:
                await conn.execute(
                    Dummy.__table__.update()  # type: ignore[union-attr]
                    .where(Dummy.id == row.id)
                    .values(uuid=str(uuid_module.uuid4()))
                )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    configure_logging(settings)
    tracer_provider = setup_otel(settings)
    engine = get_engine(settings)
    if is_local_dev_mode(settings):
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await _backfill_dummy_uuids(engine)
    try:
        yield
    finally:
        await dispose_engine()
        tracer_provider.shutdown()


app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
    root_path=settings.root_path,
    lifespan=lifespan,
)

if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,  # ty: ignore[invalid-argument-type]
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
        expose_headers=settings.cors_expose_headers_list,
    )

app.state.limiter = limiter
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(v1_router)
app.include_router(v2_router)


@app.get(HEALTH_PATH, tags=["Infrastructure"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")
setup_prometheus(app)
