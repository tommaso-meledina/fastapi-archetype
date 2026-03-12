# Epic 23: Logging Overhaul & Test Cleanup

Migrate from the custom logging infrastructure to structlog and streamline the test suite by removing dedicated mock-implementation tests and reorganizing large test classes (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 21–26).

## Context

The current `observability/logging.py` implements a custom `SpanFilter`, `PlainFormatter`, `JsonFormatter`, and secret redaction pipeline using `logging.config.dictConfig`. After comparing loguru and structlog against the project's existing features (two output modes, OTEL trace correlation, secret redaction, per-module loggers), structlog was selected: its processor pipeline maps almost 1-to-1 to the custom code already in place.

On the test side, dedicated unit tests exist for mock service implementations, which adds maintenance cost without proportional value. Large test classes in some modules make navigation harder than separate files.

## Problem Statement

- **Custom logging code:** `SpanFilter`, `PlainFormatter`, `JsonFormatter`, and secret redaction are hand-rolled; structlog provides equivalent processors out of the box or with minimal wrappers.
- **Mock implementation tests:** Testing the mocks themselves is wasteful; one profile-switching integration test per service version is sufficient.
- **Large test classes:** Some test files use classes to group tests; separate files are more Pythonic and easier to navigate with pytest.

## Proposed Epic Goal

1. Add `structlog` as a runtime dependency.
2. Rewrite `observability/logging.py` with a structlog processor pipeline.
3. Simplify `logging_decorator.py` in light of structlog's `bind()`/contextvars.
4. Remove dedicated mock-implementation unit tests; retain one profile-switching integration test per service version.
5. Exclude mock implementation files from coverage configuration.
6. Reorganize large test classes into separate files.

## Success Criteria

- `structlog` is a runtime dependency in `pyproject.toml`.
- `observability/logging.py` uses structlog processors; `SpanFilter`, `PlainFormatter`, `JsonFormatter` no longer exist as custom classes.
- `logging_decorator.py` is simplified (exact scope determined during implementation; AOP `apply_logging` remains).
- No dedicated mock-implementation unit tests remain; one profile-switching integration test per service version exists.
- `pyproject.toml` coverage config excludes mock implementation files.
- Large test classes are split into separate files.
- All quality checks pass.

## Stories

### Story 23.1: structlog Migration

As a **developer**,
I want **the logging infrastructure rewritten with structlog processors replacing the custom formatters and filters**,
so that **logging is maintained via a well-supported library instead of bespoke code**.

**Acceptance Criteria:**

- **Given** `pyproject.toml` **When** I inspect runtime dependencies **Then** `structlog` is listed.
- **Given** `observability/logging.py` **When** I inspect it **Then** it configures a structlog processor pipeline that provides:
  - Two output modes (`plain` and `json`) selectable via `LOG_MODE`.
  - OTEL trace/span ID injection (replacing `SpanFilter`).
  - Secret redaction (replacing the custom redaction logic).
  - Per-module logger support via `structlog.get_logger()` or stdlib integration.
- **Given** `observability/logging.py` **When** I search for `SpanFilter`, `PlainFormatter`, `JsonFormatter` **Then** these custom classes no longer exist.
- **Given** `aop/logging_decorator.py` **When** I inspect it **Then** it is simplified where structlog's `bind()`/contextvars capabilities reduce boilerplate. The `apply_logging(module)` mechanism remains as a separate concern (AOP is orthogonal to the logging backend).
- **Given** the application running with `LOG_MODE=plain` or `LOG_MODE=json` **When** requests are made **Then** log output matches the documented format contracts (UTC ISO-8601, traceId/spanId, camelCase JSON fields, etc.).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 23.2: Test Suite Cleanup

As a **developer**,
I want **dedicated mock-implementation tests removed, mock files excluded from coverage, and large test classes split into files**,
so that **the test suite is leaner and follows pytest conventions**.

**Acceptance Criteria:**

- **Given** `tests/services/` **When** I inspect it **Then** no dedicated unit tests for mock service implementations exist (e.g. no test file that only exercises `MockDummyServiceV1` methods in isolation).
- **Given** `tests/services/` **When** I inspect it **Then** at least one integration test per service version (v1, v2) verifies that profile-switching works (i.e. `PROFILE=mock` wires the mock and `PROFILE=default` wires the default).
- **Given** `pyproject.toml` **When** I inspect coverage configuration **Then** mock implementation files (e.g. `mock_dummy_service.py`) are excluded from coverage measurement.
- **Given** `tests/observability/` and `tests/auth/` **When** I inspect them **Then** formerly large test classes are reorganized into separate files (one logical grouping per file).
- **Given** the test suite **When** I run all quality checks **Then** all pass **And** coverage remains at or above the project target (>90%).
