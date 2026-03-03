from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.core.errors import (
    AppException,
    ErrorCode,
    _build_error_body,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_error_code_not_found() -> None:
    assert ErrorCode.NOT_FOUND.code == "NOT_FOUND"
    assert ErrorCode.NOT_FOUND.message == "Resource not found"
    assert ErrorCode.NOT_FOUND.http_status == 404


def test_error_code_validation_error() -> None:
    assert ErrorCode.VALIDATION_ERROR.code == "VALIDATION_ERROR"
    assert ErrorCode.VALIDATION_ERROR.http_status == 422


def test_error_code_internal_error() -> None:
    assert ErrorCode.INTERNAL_ERROR.code == "INTERNAL_ERROR"
    assert ErrorCode.INTERNAL_ERROR.http_status == 500


def test_error_code_dummy_not_found() -> None:
    assert ErrorCode.DUMMY_NOT_FOUND.code == "DUMMY_NOT_FOUND"
    assert ErrorCode.DUMMY_NOT_FOUND.http_status == 404


def test_app_exception_carries_error_code() -> None:
    exc = AppException(ErrorCode.NOT_FOUND)
    assert exc.error_code is ErrorCode.NOT_FOUND
    assert exc.detail is None
    assert str(exc) == "Resource not found"


def test_app_exception_with_detail() -> None:
    exc = AppException(ErrorCode.DUMMY_NOT_FOUND, detail="id=99")
    assert exc.detail == "id=99"
    assert exc.error_code is ErrorCode.DUMMY_NOT_FOUND


def test_build_error_body_structure() -> None:
    body = _build_error_body("TEST_CODE", "Test message", "extra detail")
    assert body == {
        "errorCode": "TEST_CODE",
        "message": "Test message",
        "detail": "extra detail",
    }


def test_build_error_body_null_detail() -> None:
    body = _build_error_body("CODE", "msg")
    assert body["detail"] is None


def test_validation_error_via_http(client: TestClient) -> None:
    response = client.post("/dummies")
    assert response.status_code == 422
    data = response.json()
    assert data["errorCode"] == "VALIDATION_ERROR"
    assert data["message"] == "Request validation failed"
    assert "detail" in data
