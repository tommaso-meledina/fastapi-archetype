from __future__ import annotations

import logging
from types import ModuleType

import pytest

from fastapi_archetype.aop.logging_decorator import apply_logging, log_io


def test_log_io_logs_inputs(caplog: pytest.LogCaptureFixture) -> None:
    @log_io
    def add(a: int, b: int) -> int:
        return a + b

    with caplog.at_level(logging.DEBUG):
        result = add(1, 2)

    assert result == 3
    assert "add invoked with args" in caplog.text
    assert "a=1" in caplog.text
    assert "b=2" in caplog.text


def test_log_io_logs_return_value(caplog: pytest.LogCaptureFixture) -> None:
    @log_io
    def greet(name: str) -> str:
        return f"Hello {name}"

    with caplog.at_level(logging.DEBUG):
        result = greet("World")

    assert result == "Hello World"
    assert "greet returned" in caplog.text
    assert "'Hello World'" in caplog.text


def test_log_io_preserves_function_metadata() -> None:
    @log_io
    def my_func() -> None:
        """My docstring."""

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "My docstring."


def test_apply_logging_wraps_public_functions() -> None:
    mod = ModuleType("test_mod")
    mod.__name__ = "test_mod"

    def public_func() -> int:
        return 42

    public_func.__module__ = "test_mod"
    mod.public_func = public_func  # ty: ignore[unresolved-attribute]

    apply_logging(mod)
    assert hasattr(mod.public_func, "__wrapped__")
    assert mod.public_func() == 42


def test_apply_logging_skips_private_functions() -> None:
    mod = ModuleType("test_mod")
    mod.__name__ = "test_mod"

    def _private() -> int:
        return 0

    _private.__module__ = "test_mod"
    mod._private = _private  # ty: ignore[unresolved-attribute]

    apply_logging(mod)
    assert not hasattr(mod._private, "__wrapped__")


def test_log_io_logs_exception_at_error(caplog: pytest.LogCaptureFixture) -> None:
    @log_io
    def explode() -> None:
        raise ValueError("boom")

    with caplog.at_level(logging.DEBUG), pytest.raises(ValueError, match="boom"):
        explode()

    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(error_records) == 1
    assert "explode raised" in error_records[0].message
    assert "ValueError: boom" in error_records[0].message


def test_apply_logging_skips_reexported_imports() -> None:
    mod = ModuleType("test_mod")
    mod.__name__ = "test_mod"

    def foreign_func() -> int:
        return 1

    foreign_func.__module__ = "other_module"
    mod.foreign_func = foreign_func  # ty: ignore[unresolved-attribute]

    apply_logging(mod)
    assert not hasattr(mod.foreign_func, "__wrapped__")
