import logging

import structlog
from fastapi.testclient import TestClient

from fastapi_archetype.observability.logging import (
    NO_SPAN_ID,
    NO_TRACE_ID,
    _current_span_ids,
)


class TestExistingConventions:
    def test_getlogger_pattern_works(self) -> None:
        lgr = logging.getLogger(__name__)
        assert lgr.name == __name__

    def test_structlog_getlogger_works(self) -> None:
        lgr = structlog.get_logger(__name__)
        assert lgr is not None

    def test_aop_compatibility(self) -> None:
        from fastapi_archetype.aop.logging_decorator import log_io

        @log_io
        def sample(x: int) -> int:
            return x * 2

        assert sample(3) == 6


class TestTraceCorrelationDuringRequest:
    def test_request_carries_real_trace_and_span_ids(self, client: TestClient) -> None:
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
