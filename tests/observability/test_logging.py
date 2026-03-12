import json
import logging
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import pytest
import structlog
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.observability.logging import (
    NO_SPAN_ID,
    NO_TRACE_ID,
    _add_timestamp,
    _extract_exc_info,
    _inject_trace_context,
    _json_renderer,
    _plain_renderer,
    _redact_secrets,
    configure_logging,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_CTX = SpanContext(
    trace_id=0xABCDEF1234567890ABCDEF1234567890,
    span_id=0x1234567890ABCDEF,
    is_remote=False,
    trace_flags=TraceFlags(TraceFlags.SAMPLED),
)


def _base_event(
    message: str = "test message",
    level: str = "info",
    logger_name: str = "test.logger",
    **extra: Any,
) -> MutableMapping[str, Any]:
    """Build a minimal event dict as structlog processors would see it."""
    ed: MutableMapping[str, Any] = {
        "event": message,
        "level": level,
        "logger": logger_name,
        "timestamp": "2024-01-01T00:00:00+00:00",
        "traceId": NO_TRACE_ID,
        "spanId": NO_SPAN_ID,
    }
    ed.update(extra)
    return ed


def _make_record(name: str, msg: str, level: int = logging.INFO) -> logging.LogRecord:
    record = logging.LogRecord(name, level, "test.py", 1, msg, (), None)
    return record


# ---------------------------------------------------------------------------
# Story 12.1 — LOG_MODE configuration and toggle
# ---------------------------------------------------------------------------


class TestLogModeConfiguration:
    def test_default_log_mode_is_plain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LOG_MODE", raising=False)
        settings = AppSettings()
        assert settings.log_mode == "plain"

    def test_json_mode_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_MODE", "json")
        settings = AppSettings()
        assert settings.log_mode == "json"

    def test_invalid_mode_falls_back_to_plain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_MODE", "yaml")
        with pytest.warns(UserWarning, match="Invalid LOG_MODE 'yaml'"):
            settings = AppSettings()
        assert settings.log_mode == "plain"

    def test_mode_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_MODE", "JSON")
        settings = AppSettings()
        assert settings.log_mode == "json"

    def test_configure_logging_plain_uses_processor_formatter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_MODE", "plain")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        assert any(
            isinstance(h.formatter, structlog.stdlib.ProcessorFormatter)
            for h in root.handlers
        )

    def test_configure_logging_plain_uses_plain_renderer(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_MODE", "plain")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        pf = next(
            h.formatter
            for h in root.handlers
            if isinstance(h.formatter, structlog.stdlib.ProcessorFormatter)
        )
        assert pf.processors[-1] is _plain_renderer

    def test_configure_logging_json_uses_json_renderer(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_MODE", "json")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        pf = next(
            h.formatter
            for h in root.handlers
            if isinstance(h.formatter, structlog.stdlib.ProcessorFormatter)
        )
        assert pf.processors[-1] is _json_renderer


# ---------------------------------------------------------------------------
# Story 12.2 — Format contracts and trace/span correlation
# ---------------------------------------------------------------------------


class TestPlainRenderer:
    def test_plain_format_fields(self) -> None:
        ed = _base_event("hello world", logger_name="test.plain")
        output = _plain_renderer(None, "info", ed)
        assert f"[{NO_TRACE_ID}]" in output
        assert f"[{NO_SPAN_ID}]" in output
        assert "INFO" in output
        assert "test.plain" in output
        assert "hello world" in output

    def test_plain_trace_id_and_span_id_in_brackets(self) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            ed = _base_event("with span")
            _inject_trace_context(None, "info", ed)
            output = _plain_renderer(None, "info", ed)
            assert f"[{ed['traceId']}]" in output
            assert f"[{ed['spanId']}]" in output

    def test_plain_format_utc_iso8601(self) -> None:
        record = _make_record("test.ts", "ts check")
        ts_dict: MutableMapping[str, Any] = {"event": "ts check", "_record": record}
        _add_timestamp(None, "info", ts_dict)
        ed = {**_base_event("ts check"), "timestamp": ts_dict["timestamp"]}
        output = _plain_renderer(None, "info", ed)
        timestamp = output.split(" ")[0]
        assert "+00:00" in timestamp or timestamp.endswith("Z")


class TestJsonRenderer:
    def test_json_format_is_valid_json(self) -> None:
        ed = _base_event("json test")
        output = _json_renderer(None, "info", ed)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_format_required_fields(self) -> None:
        ed = _base_event("field check")
        parsed = json.loads(_json_renderer(None, "info", ed))
        for field in ("timestamp", "level", "logger", "message", "traceId", "spanId"):
            assert field in parsed

    def test_json_format_camel_case(self) -> None:
        ed = _base_event("case check")
        parsed = json.loads(_json_renderer(None, "info", ed))
        assert "traceId" in parsed
        assert "spanId" in parsed
        assert "trace_id" not in parsed
        assert "span_id" not in parsed

    def test_json_format_utc_iso8601(self) -> None:
        ed = _base_event("ts check", timestamp="2024-06-15T12:00:00+00:00")
        parsed = json.loads(_json_renderer(None, "info", ed))
        assert "+00:00" in parsed["timestamp"]

    def test_json_span_id_populated_with_active_span(self) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            ed = _base_event("span check")
            _inject_trace_context(None, "info", ed)
            parsed = json.loads(_json_renderer(None, "info", ed))
            assert parsed["spanId"] != NO_SPAN_ID
            assert len(parsed["spanId"]) == 16


class TestTraceCorrelation:
    def test_no_trace_context_yields_placeholders(self) -> None:
        ed: MutableMapping[str, Any] = {"event": "no span"}
        _inject_trace_context(None, "info", ed)
        assert ed["traceId"] == NO_TRACE_ID
        assert ed["spanId"] == NO_SPAN_ID

    def test_active_span_injects_both_ids(self) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            ed: MutableMapping[str, Any] = {"event": "traced"}
            _inject_trace_context(None, "info", ed)
            assert ed["traceId"] != NO_TRACE_ID
            assert len(ed["traceId"]) == 32
            assert ed["spanId"] != NO_SPAN_ID
            assert len(ed["spanId"]) == 16

    def test_invalid_span_context_yields_placeholders(self) -> None:
        invalid_ctx = SpanContext(
            trace_id=0,
            span_id=0,
            is_remote=False,
            trace_flags=TraceFlags(0),
        )
        span = NonRecordingSpan(invalid_ctx)
        with trace.use_span(span):
            ed: MutableMapping[str, Any] = {"event": "invalid ctx"}
            _inject_trace_context(None, "info", ed)
            assert ed["traceId"] == NO_TRACE_ID
            assert ed["spanId"] == NO_SPAN_ID


# ---------------------------------------------------------------------------
# Story 12.3 — Exception interface and secret redaction
# ---------------------------------------------------------------------------


class TestExceptionPlainMode:
    def test_plain_exception_includes_message(self) -> None:
        try:
            raise ValueError("something broke")
        except ValueError:
            ei = sys.exc_info()

        ed = _base_event("op failed", exc_info=ei)
        output = _plain_renderer(None, "error", ed)
        assert "ValueError: something broke" in output

    def test_plain_exception_no_full_traceback(self) -> None:
        try:
            raise RuntimeError("bad state")
        except RuntimeError:
            ei = sys.exc_info()

        ed = _base_event("op failed", exc_info=ei)
        output = _plain_renderer(None, "error", ed)
        assert "Traceback" not in output
        assert "RuntimeError: bad state" in output


class TestExceptionJsonMode:
    def test_json_exception_structured_fields(self) -> None:
        try:
            raise TypeError("wrong type")
        except TypeError:
            ei = sys.exc_info()

        ed = _base_event("op failed", exc_info=ei)
        parsed = json.loads(_json_renderer(None, "error", ed))
        assert parsed["exceptionType"] == "TypeError"
        assert parsed["exceptionMessage"] == "wrong type"
        assert isinstance(parsed["stackTrace"], list)
        assert len(parsed["stackTrace"]) > 0

    def test_json_no_exception_no_extra_fields(self) -> None:
        ed = _base_event("normal msg")
        parsed = json.loads(_json_renderer(None, "info", ed))
        assert "exceptionType" not in parsed
        assert "stackTrace" not in parsed


class TestExcInfoExtraction:
    def test_extract_exc_info_from_log_record(self) -> None:
        try:
            raise ValueError("test error")
        except ValueError:
            ei = sys.exc_info()

        record = _make_record("test", "msg", logging.ERROR)
        record.exc_info = ei
        ed: MutableMapping[str, Any] = {"event": "msg", "_record": record}
        _extract_exc_info(None, "error", ed)

        assert "exc_info" in ed
        assert ed["exc_info"][1] is ei[1]
        assert record.exc_info is None

    def test_extract_exc_info_no_exception(self) -> None:
        record = _make_record("test", "no exc")
        record.exc_info = None
        ed: MutableMapping[str, Any] = {"event": "no exc", "_record": record}
        _extract_exc_info(None, "info", ed)
        assert "exc_info" not in ed


class TestSecretRedaction:
    @pytest.mark.parametrize(
        "text,expected_redacted",
        [
            ("password=hunter2", "password=***"),
            ("token: abc123xyz", "token: ***"),
            ("api_key=sk-live-12345", "api_key=***"),
            ("apikey=secret", "apikey=***"),
            ("Authorization: Bearer eyJhbGciOi", "Authorization: ***"),
            ("credential=mysecret", "credential=***"),
            ("secret=shh", "secret=***"),
        ],
    )
    def test_redact_known_secret_patterns(
        self, text: str, expected_redacted: str
    ) -> None:
        assert _redact_secrets(text) == expected_redacted

    def test_non_secret_text_unchanged(self) -> None:
        text = "user created id=42 name=Alice"
        assert _redact_secrets(text) == text

    def test_plain_mode_redacts_secrets(self) -> None:
        ed = _base_event("auth password=hunter2 done")
        output = _plain_renderer(None, "info", ed)
        assert "hunter2" not in output
        assert "password=***" in output

    def test_json_mode_redacts_secrets(self) -> None:
        ed = _base_event("got token=abc123")
        parsed = json.loads(_json_renderer(None, "info", ed))
        assert "abc123" not in parsed["message"]
        assert "***" in parsed["message"]


class TestExistingConventions:
    def test_getlogger_pattern_works(self) -> None:
        lgr = logging.getLogger(__name__)
        assert lgr.name == __name__

    def test_structlog_getlogger_works(self) -> None:
        lgr = structlog.get_logger(__name__)
        assert lgr is not None

    def test_log_level_respected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("LOG_MODE", "plain")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_aop_compatibility(self) -> None:
        from fastapi_archetype.aop.logging_decorator import log_io

        @log_io
        def sample(x: int) -> int:
            return x * 2

        assert sample(3) == 6


class TestTraceCorrelationDuringRequest:
    def test_request_carries_real_trace_and_span_ids(self, client: TestClient) -> None:
        from fastapi_archetype.observability.logging import _current_span_ids

        captured: list[tuple[str, str]] = []

        class _Capture(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                captured.append(_current_span_ids())
                return True

        stub_logger = logging.getLogger("fastapi_archetype.test_stubs")
        capture = _Capture()
        stub_logger.addFilter(capture)
        original_level = stub_logger.level
        stub_logger.setLevel(logging.DEBUG)
        try:
            client.get("/test/open")
        finally:
            stub_logger.removeFilter(capture)
            stub_logger.setLevel(original_level)

        assert len(captured) > 0, "Expected stub log during the request"
        assert all(tid != NO_TRACE_ID and sid != NO_SPAN_ID for tid, sid in captured), (
            f"Expected real trace/span IDs, got: {captured}"
        )


class TestAddTimestamp:
    def test_timestamp_from_log_record(self) -> None:
        record = _make_record("test", "msg")
        ed: MutableMapping[str, Any] = {"event": "msg", "_record": record}
        _add_timestamp(None, "info", ed)
        assert "timestamp" in ed
        assert "+00:00" in ed["timestamp"] or ed["timestamp"].endswith("Z")

    def test_timestamp_without_record(self) -> None:
        ed: MutableMapping[str, Any] = {"event": "msg"}
        _add_timestamp(None, "info", ed)
        assert "timestamp" in ed
        ts = cast(str, ed["timestamp"])
        assert "+00:00" in ts or ts.endswith("Z")
