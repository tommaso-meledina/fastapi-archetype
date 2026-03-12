import json
import logging
import sys

import pytest
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.observability.logging import (  # noinspection PyProtectedMember
    NO_SPAN_ID,
    NO_TRACE_ID,
    JsonFormatter,
    PlainFormatter,
    SpanFilter,
    _redact_secrets,
    configure_logging,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_VALID_CTX = SpanContext(
    trace_id=0xABCDEF1234567890ABCDEF1234567890,
    span_id=0x1234567890ABCDEF,
    is_remote=False,
    trace_flags=TraceFlags(TraceFlags.SAMPLED),
)


@pytest.fixture()
def plain_logger() -> logging.Logger:
    lgr = logging.getLogger("test.plain")
    lgr.handlers.clear()
    lgr.propagate = False
    handler = logging.StreamHandler()
    handler.addFilter(SpanFilter())
    handler.setFormatter(PlainFormatter())
    lgr.addHandler(handler)
    lgr.setLevel(logging.DEBUG)
    return lgr


@pytest.fixture()
def json_logger() -> logging.Logger:
    lgr = logging.getLogger("test.json")
    lgr.handlers.clear()
    lgr.propagate = False
    handler = logging.StreamHandler()
    handler.addFilter(SpanFilter())
    handler.setFormatter(JsonFormatter())
    lgr.addHandler(handler)
    lgr.setLevel(logging.DEBUG)
    return lgr


def _make_record(
    lgr: logging.Logger, msg: str, level: int = logging.INFO
) -> logging.LogRecord:
    record = lgr.makeRecord(lgr.name, level, "test.py", 1, msg, (), None)
    SpanFilter().filter(record)
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

    def test_configure_logging_plain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_MODE", "plain")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        assert any(isinstance(h.formatter, PlainFormatter) for h in root.handlers)

    def test_configure_logging_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_MODE", "json")
        settings = AppSettings()
        configure_logging(settings)
        root = logging.getLogger()
        assert any(isinstance(h.formatter, JsonFormatter) for h in root.handlers)


# ---------------------------------------------------------------------------
# Story 12.2 — Format contracts and trace/span correlation
# ---------------------------------------------------------------------------


class TestPlainFormatter:
    def test_plain_format_fields(self, plain_logger: logging.Logger) -> None:
        record = _make_record(plain_logger, "hello world")
        output = PlainFormatter().format(record)
        assert f"[{NO_TRACE_ID}]" in output
        assert f"[{NO_SPAN_ID}]" in output
        assert "INFO" in output
        assert "test.plain" in output
        assert "hello world" in output

    def test_plain_trace_id_and_span_id_in_brackets(
        self, plain_logger: logging.Logger
    ) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            record = _make_record(plain_logger, "with span")
            output = PlainFormatter().format(record)
            tid = record.traceId  # type: ignore[attr-defined]
            sid = record.spanId  # type: ignore[attr-defined]
            assert f"[{tid}]" in output
            assert f"[{sid}]" in output

    def test_plain_format_utc_iso8601(self, plain_logger: logging.Logger) -> None:
        record = _make_record(plain_logger, "ts check")
        output = PlainFormatter().format(record)
        timestamp = output.split(" ")[0]
        assert "+00:00" in timestamp or timestamp.endswith("Z")


class TestJsonFormatter:
    def test_json_format_is_valid_json(self, json_logger: logging.Logger) -> None:
        record = _make_record(json_logger, "json test")
        output = JsonFormatter().format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_format_required_fields(self, json_logger: logging.Logger) -> None:
        record = _make_record(json_logger, "field check")
        parsed = json.loads(JsonFormatter().format(record))
        for field in (
            "timestamp",
            "level",
            "logger",
            "message",
            "traceId",
            "spanId",
        ):
            assert field in parsed

    def test_json_format_camel_case(self, json_logger: logging.Logger) -> None:
        record = _make_record(json_logger, "case check")
        parsed = json.loads(JsonFormatter().format(record))
        assert "traceId" in parsed
        assert "spanId" in parsed
        assert "trace_id" not in parsed
        assert "span_id" not in parsed

    def test_json_format_utc_iso8601(self, json_logger: logging.Logger) -> None:
        record = _make_record(json_logger, "ts check")
        parsed = json.loads(JsonFormatter().format(record))
        assert "+00:00" in parsed["timestamp"]

    def test_json_span_id_populated_with_active_span(
        self, json_logger: logging.Logger
    ) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            record = _make_record(json_logger, "span check")
            parsed = json.loads(JsonFormatter().format(record))
            assert parsed["spanId"] != NO_SPAN_ID
            assert len(parsed["spanId"]) == 16


class TestTraceCorrelation:
    def test_no_trace_context_yields_placeholders(
        self, plain_logger: logging.Logger
    ) -> None:
        record = _make_record(plain_logger, "no span")
        assert record.traceId == NO_TRACE_ID  # type: ignore[attr-defined]
        assert record.spanId == NO_SPAN_ID  # type: ignore[attr-defined]

    def test_active_span_injects_both_ids(self, plain_logger: logging.Logger) -> None:
        span = NonRecordingSpan(_VALID_CTX)
        with trace.use_span(span):
            record = _make_record(plain_logger, "traced")
            assert record.traceId != NO_TRACE_ID  # type: ignore[attr-defined]
            assert len(record.traceId) == 32  # type: ignore[attr-defined]
            assert record.spanId != NO_SPAN_ID  # type: ignore[attr-defined]
            assert len(record.spanId) == 16  # type: ignore[attr-defined]

    def test_invalid_span_context_yields_placeholders(
        self, plain_logger: logging.Logger
    ) -> None:
        invalid_ctx = SpanContext(
            trace_id=0,
            span_id=0,
            is_remote=False,
            trace_flags=TraceFlags(0),
        )
        span = NonRecordingSpan(invalid_ctx)
        with trace.use_span(span):
            record = _make_record(plain_logger, "invalid ctx")
            assert record.traceId == NO_TRACE_ID  # type: ignore[attr-defined]
            assert record.spanId == NO_SPAN_ID  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Story 12.3 — Exception interface and secret redaction
# ---------------------------------------------------------------------------


class TestExceptionPlainMode:
    def test_plain_exception_includes_message(
        self, plain_logger: logging.Logger
    ) -> None:
        try:
            raise ValueError("something broke")
        except ValueError:
            ei = sys.exc_info()
            record = plain_logger.makeRecord(
                plain_logger.name,
                logging.ERROR,
                "test.py",
                1,
                "op failed",
                (),
                ei,
            )
        SpanFilter().filter(record)
        output = PlainFormatter().format(record)
        assert "ValueError: something broke" in output

    def test_plain_exception_no_full_traceback(
        self, plain_logger: logging.Logger
    ) -> None:
        try:
            raise RuntimeError("bad state")
        except RuntimeError:
            ei = sys.exc_info()
            record = plain_logger.makeRecord(
                plain_logger.name,
                logging.ERROR,
                "test.py",
                1,
                "op failed",
                (),
                ei,
            )
        SpanFilter().filter(record)
        output = PlainFormatter().format(record)
        assert "Traceback" not in output
        assert "RuntimeError: bad state" in output


class TestExceptionJsonMode:
    def test_json_exception_structured_fields(
        self, json_logger: logging.Logger
    ) -> None:
        try:
            raise TypeError("wrong type")
        except TypeError:
            ei = sys.exc_info()
            record = json_logger.makeRecord(
                json_logger.name,
                logging.ERROR,
                "test.py",
                1,
                "op failed",
                (),
                ei,
            )
        SpanFilter().filter(record)
        parsed = json.loads(JsonFormatter().format(record))
        assert parsed["exceptionType"] == "TypeError"
        assert parsed["exceptionMessage"] == "wrong type"
        assert isinstance(parsed["stackTrace"], list)
        assert len(parsed["stackTrace"]) > 0

    def test_json_no_exception_no_extra_fields(
        self, json_logger: logging.Logger
    ) -> None:
        record = _make_record(json_logger, "normal msg")
        parsed = json.loads(JsonFormatter().format(record))
        assert "exceptionType" not in parsed
        assert "stackTrace" not in parsed


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

    def test_plain_mode_redacts_secrets(self, plain_logger: logging.Logger) -> None:
        record = _make_record(plain_logger, "auth password=hunter2 done")
        output = PlainFormatter().format(record)
        assert "hunter2" not in output
        assert "password=***" in output

    def test_json_mode_redacts_secrets(self, json_logger: logging.Logger) -> None:
        record = _make_record(json_logger, "got token=abc123")
        parsed = json.loads(JsonFormatter().format(record))
        assert "abc123" not in parsed["message"]
        assert "***" in parsed["message"]


class TestExistingConventions:
    def test_getlogger_pattern_works(self) -> None:
        lgr = logging.getLogger(__name__)
        assert lgr.name == __name__

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
