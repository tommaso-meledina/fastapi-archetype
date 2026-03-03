from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.core.database import get_engine
from fastapi_archetype.core.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
