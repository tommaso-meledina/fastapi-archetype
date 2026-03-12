# Story 23.1: structlog Migration

**Status:** in-progress

## Story

As a **developer**,
I want **the logging infrastructure rewritten with structlog processors replacing the custom formatters and filters**,
so that **logging is maintained via a well-supported library instead of bespoke code**.

## Acceptance Criteria

- **Given** `pyproject.toml` **When** I inspect runtime dependencies **Then** `structlog` is listed.
- **Given** `observability/logging.py` **When** I inspect it **Then** it configures a structlog processor pipeline that provides:
  - Two output modes (`plain` and `json`) selectable via `LOG_MODE`.
  - OTEL trace/span ID injection (replacing `SpanFilter`).
  - Secret redaction (replacing the custom redaction logic).
  - Per-module logger support via `structlog.get_logger()` or stdlib integration.
- **Given** `observability/logging.py` **When** I search for `SpanFilter`, `PlainFormatter`, `JsonFormatter` **Then** these custom classes no longer exist.
- **Given** `aop/logging_decorator.py` **When** I inspect it **Then** it is simplified where structlog's capabilities reduce boilerplate. The `apply_logging(module)` mechanism remains.
- **Given** the application running with `LOG_MODE=plain` or `LOG_MODE=json` **When** requests are made **Then** log output matches the documented format contracts (UTC ISO-8601, traceId/spanId, camelCase JSON fields, etc.).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Add `structlog` runtime dependency to `pyproject.toml`
- [x] Rewrite `observability/logging.py` with structlog processor pipeline
- [x] Simplify `aop/logging_decorator.py` (use `structlog.get_logger`, fix except syntax)
- [x] Update `tests/observability/test_logging.py` for new structlog-based API
- [x] All quality checks pass
