import enum
from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


class ErrorCode(enum.Enum):
    INTERNAL_ERROR = ("INTERNAL_ERROR", "An unexpected error occurred", 500)
    RATE_LIMITED = ("RATE_LIMITED", "Rate limit exceeded", 429)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "Request validation failed", 422)
    BAD_REQUEST = ("BAD_REQUEST", "Bad request", 400)
    NOT_FOUND = ("NOT_FOUND", "Resource not found", 404)
    DUMMY_NOT_FOUND = ("DUMMY_NOT_FOUND", "Dummy not found", 404)
    UNAUTHORIZED = ("UNAUTHORIZED", "Authentication required", 401)
    FORBIDDEN = ("FORBIDDEN", "Access forbidden", 403)

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


async def app_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    app_exc = cast(AppException, exc)
    return JSONResponse(
        status_code=app_exc.error_code.http_status,
        content=_build_error_body(
            app_exc.error_code.code, app_exc.error_code.message, app_exc.detail
        ),
    )


async def rate_limit_exceeded_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    rate_exc = cast(RateLimitExceeded, exc)
    return JSONResponse(
        status_code=ErrorCode.RATE_LIMITED.http_status,
        content=_build_error_body(
            ErrorCode.RATE_LIMITED.code,
            ErrorCode.RATE_LIMITED.message,
            str(rate_exc.detail),
        ),
    )


async def validation_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    val_exc = cast(RequestValidationError, exc)
    return JSONResponse(
        status_code=ErrorCode.VALIDATION_ERROR.http_status,
        content=_build_error_body(
            ErrorCode.VALIDATION_ERROR.code,
            ErrorCode.VALIDATION_ERROR.message,
            str(val_exc.errors()),
        ),
    )
