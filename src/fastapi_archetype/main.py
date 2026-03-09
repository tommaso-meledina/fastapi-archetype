from __future__ import annotations

import uuid as uuid_module
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, SQLModel, select

from fastapi_archetype.api.v1 import router as v1_router
from fastapi_archetype.api.v2 import router as v2_router
from fastapi_archetype.core.config import AppSettings
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

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.engine import Engine


def _backfill_dummy_uuids(engine: Engine) -> None:
    with Session(engine) as session:
        for d in session.exec(select(Dummy)).all():
            if not d.uuid:
                d.uuid = str(uuid_module.uuid4())
        session.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    _settings = AppSettings()
    configure_logging(_settings)
    tracer_provider = setup_otel(_settings)
    engine = get_engine(_settings)
    # Table creation only in local/dev mode (SQLite). Other backends rely on
    # their own init/migrations (e.g. compose/mariadb/init), not the app.
    if is_local_dev_mode(_settings):
        SQLModel.metadata.create_all(engine)
        _backfill_dummy_uuids(engine)
    try:
        yield
    finally:
        dispose_engine()
        tracer_provider.shutdown()


settings = AppSettings()
app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
    root_path=settings.root_path,
    lifespan=lifespan,
)

if settings.cors_enabled:
    # Starlette stub expects _MiddlewareFactory; CORSMiddleware valid at runtime.
    app.add_middleware(
        CORSMiddleware,  # ty: ignore[invalid-argument-type]
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
        expose_headers=settings.cors_expose_headers_list,
    )

app.state.limiter = limiter
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.include_router(v1_router)
app.include_router(v2_router)


@app.get(HEALTH_PATH, tags=["Infrastructure"])
def health() -> dict[str, str]:
    return {"status": "ok"}


FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")
setup_prometheus(app)
