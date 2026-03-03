from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel

from fastapi_archetype.api.dummy_routes import router as dummy_router
from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.database import get_engine
from fastapi_archetype.core.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
)
from fastapi_archetype.observability.otel import setup_otel
from fastapi_archetype.observability.prometheus import setup_prometheus

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stdout,
        force=True,
    )
    tracer_provider = setup_otel(app, settings)
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    yield
    tracer_provider.shutdown()


app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.include_router(dummy_router)

setup_prometheus(app)
