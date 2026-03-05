from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from sqlmodel import SQLModel

from fastapi_archetype.api.v1 import router as v1_router
from fastapi_archetype.api.v2 import router as v2_router
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.constants import HEALTH_PATH
from fastapi_archetype.core.database import dispose_engine, get_engine
from fastapi_archetype.core.errors import (
    AppException,
    app_exception_handler,
    rate_limit_exceeded_handler,
    validation_exception_handler,
)
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.observability.logging import configure_logging
from fastapi_archetype.observability.otel import setup_otel
from fastapi_archetype.observability.prometheus import setup_prometheus

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    configure_logging(settings)
    tracer_provider = setup_otel(app, settings)
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    try:
        yield
    finally:
        dispose_engine()
        tracer_provider.shutdown()


app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
    root_path=AppSettings().root_path,
    lifespan=lifespan,
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


setup_prometheus(app)
