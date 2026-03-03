from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from fastapi import Request
    from fastapi.exceptions import RequestValidationError


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = ("INTERNAL_ERROR", "An unexpected error occurred", 500)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "Request validation failed", 422)
    NOT_FOUND = ("NOT_FOUND", "Resource not found", 404)
    DUMMY_NOT_FOUND = ("DUMMY_NOT_FOUND", "Dummy not found", 404)

    def __init__(self, code: str, message: str, http_status: int) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status


class AppException(Exception):  # noqa: N818
    def __init__(self, error_code: ErrorCode, detail: str | None = None) -> None:
        self.error_code = error_code
        self.detail = detail
        super().__init__(error_code.message)


def _build_error_body(
    error_code: str, message: str, detail: Any = None
) -> dict[str, Any]:
    return {"errorCode": error_code, "message": message, "detail": detail}


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.error_code.http_status,
        content=_build_error_body(
            exc.error_code.code, exc.error_code.message, exc.detail
        ),
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=ErrorCode.VALIDATION_ERROR.http_status,
        content=_build_error_body(
            ErrorCode.VALIDATION_ERROR.code,
            ErrorCode.VALIDATION_ERROR.message,
            str(exc.errors()),
        ),
    )
