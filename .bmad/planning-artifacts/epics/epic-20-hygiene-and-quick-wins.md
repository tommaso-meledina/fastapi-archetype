# Epic 20: Hygiene & Quick Wins

Small, mechanical fixes with no architecture changes. Each action addresses a concrete item from the peer review feedback (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 1–9).

## Context

A peer review by experienced engineers identified several low-hanging improvements across Docker configuration, test infrastructure, model definitions, and dev tooling. These are safe, isolated changes that can be applied without altering application architecture.

## Problem Statement

- **Docker hygiene:** The Dockerfile is missing `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` environment variables, and has no configurable uvicorn worker count.
- **Test infrastructure:** `tests/auth/__init__.py` is missing (can cause import issues); test markers use `anyio` instead of the standard `asyncio` marker.
- **Model/dataclass quirks:** `_default_uuid` uses an unnecessarily complex pattern; `Principal` and `ResourceDefinition` dataclasses lack `kw_only=True`; `Principal` uses `slots=True` which prevents `__dict__` access for minimal benefit.
- **Configuration:** `log_level` uses a string with custom validation instead of an `Enum`; `ipdb` is not available in dev dependencies.

## Proposed Epic Goal

Apply all nine hygiene actions from the feedback review without breaking existing tests or changing application behaviour.

## Success Criteria

- Dockerfile sets `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` and supports env-driven `--workers` for uvicorn.
- `tests/auth/__init__.py` exists.
- `_default_uuid` is simplified to a lambda or `uuid.UUID` field type.
- `Principal` and `ResourceDefinition` dataclasses use `kw_only=True`.
- `Principal` no longer uses `slots=True`.
- `log_level` in `AppSettings` uses an `Enum`.
- `ipdb` is in dev dependencies.
- All `@pytest.mark.anyio` markers are replaced with `@pytest.mark.asyncio`; `pytest-asyncio` is in dev deps.
- All quality checks pass (`ruff check`, `ruff format --check`, `ty check`, `pytest`).

## Stories

### Story 20.1: Docker Hygiene

As a **developer or operator**,
I want **the Dockerfile to set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` and support configurable uvicorn workers**,
so that **container behaviour is predictable and logs are not lost on crashes**.

**Acceptance Criteria:**

- **Given** the `Dockerfile` **When** I inspect environment variables **Then** `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` are set.
- **Given** the `Dockerfile` **When** I inspect the uvicorn command **Then** the worker count is configurable via an environment variable (e.g. `WEB_CONCURRENCY` or `UVICORN_WORKERS`) with a sensible default (e.g. `1`).
- **Given** a built Docker image **When** I run it **Then** no `.pyc` files are created inside the container **And** stdout/stderr are unbuffered.

### Story 20.2: Test Infrastructure Fixes

As a **developer**,
I want **`tests/auth/__init__.py` to exist and all async test markers to use `@pytest.mark.asyncio`**,
so that **test discovery and async test execution follow standard pytest conventions**.

**Acceptance Criteria:**

- **Given** `tests/auth/` **When** I list files **Then** `__init__.py` exists.
- **Given** `pyproject.toml` **When** I inspect dev dependencies **Then** `pytest-asyncio` is listed.
- **Given** all test files **When** I search for `@pytest.mark.anyio` **Then** zero occurrences remain; all have been replaced with `@pytest.mark.asyncio`.
- **Given** the test suite **When** I run `uv run pytest` **Then** all tests pass.

### Story 20.3: Model and Dataclass Improvements

As a **developer**,
I want **`_default_uuid` simplified, `kw_only=True` on dataclasses, and `slots=True` removed from `Principal`**,
so that **model definitions are cleaner and more Pythonic**.

**Acceptance Criteria:**

- **Given** `models/entities/dummy.py` **When** I inspect `_default_uuid` **Then** it is a lambda or the field type is `uuid.UUID` (no `default_factory` pointing to a wrapper function).
- **Given** `auth/models.py` and `core/constants.py` **When** I inspect `Principal` and `ResourceDefinition` **Then** both dataclasses use `kw_only=True`.
- **Given** `auth/models.py` **When** I inspect `Principal` **Then** `slots=True` is not present.
- **Given** the test suite **When** I run `uv run pytest` **Then** all tests pass.

### Story 20.4: Configuration and Dev Dependencies

As a **developer**,
I want **`log_level` to use an `Enum` and `ipdb` available as a dev dependency**,
so that **config validation is type-safe and interactive debugging is readily available**.

**Acceptance Criteria:**

- **Given** `core/config.py` **When** I inspect `log_level` on `AppSettings` **Then** its type is an `Enum` (e.g. `LogLevel(str, Enum)` or `StrEnum`) with members for valid log levels **And** Pydantic validates against the enum at startup.
- **Given** `pyproject.toml` **When** I inspect dev dependencies **Then** `ipdb` is listed.
- **Given** the test suite **When** I run all quality checks **Then** all pass.
