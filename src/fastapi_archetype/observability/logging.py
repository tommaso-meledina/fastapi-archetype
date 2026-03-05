from __future__ import annotations

import json
import logging
import logging.config
import re
import traceback
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from opentelemetry import trace

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings

NO_TRACE_ID = "NO_TRACE_ID"

_REDACTED = "***"
_AUTH_HEADER_RE = re.compile(
    r"(?i)((?:authorization|bearer)\s*[=:\s]+)(\S+(?:\s+\S+)?)",
)
_SECRET_KEY_RE = re.compile(
    r"(?i)"
    r"(password|passwd|pwd|secret|token|api[_-]?key|apikey|credential)"
    r"([=:\s]+)"
    r"(\S+)",
)


def _redact_secrets(text: str) -> str:
    text = _AUTH_HEADER_RE.sub(lambda m: f"{m.group(1)}{_REDACTED}", text)
    return _SECRET_KEY_RE.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{_REDACTED}", text
    )


def _current_trace_id() -> str:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        return format(ctx.trace_id, "032x")
    return NO_TRACE_ID


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.traceId = _current_trace_id()  # type: ignore[attr-defined]
        return True


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(
            record.created, tz=UTC
        ).isoformat()
        trace_id = getattr(record, "traceId", NO_TRACE_ID)
        message = record.getMessage()
        line = f"{timestamp} [{trace_id}] {record.levelname} {record.name} {message}"

        if record.exc_info and record.exc_info[1] is not None:
            exc_type, exc_val, _ = record.exc_info
            name = exc_type.__qualname__ if exc_type else "Exception"
            line = f"{line}\n{name}: {exc_val}"
            record.exc_info = None
            record.exc_text = None

        return _redact_secrets(line)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(
            record.created, tz=UTC
        ).isoformat()
        entry: dict[str, object] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": _redact_secrets(record.getMessage()),
            "traceId": getattr(record, "traceId", NO_TRACE_ID),
        }

        if record.exc_info and record.exc_info[1] is not None:
            exc_type, exc_val, exc_tb = record.exc_info
            entry["exceptionType"] = (
                exc_type.__qualname__ if exc_type else "Exception"
            )
            entry["exceptionMessage"] = _redact_secrets(str(exc_val))
            entry["stackTrace"] = [
                _redact_secrets(line)
                for line in traceback.format_exception(
                    exc_type, exc_val, exc_tb
                )
            ]
            record.exc_info = None
            record.exc_text = None

        return json.dumps(entry, default=str)


def configure_logging(settings: AppSettings) -> None:
    config: dict[str, object] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "trace_id": {"()": TraceIdFilter},
        },
        "formatters": {
            "plain": {"()": PlainFormatter},
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": settings.log_mode,
                "filters": ["trace_id"],
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
    }
    logging.config.dictConfig(config)
