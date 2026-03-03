from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from fastapi_archetype.core.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="fastapi-archetype",
    description="A reference FastAPI application demonstrating enterprise patterns.",
)

app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
