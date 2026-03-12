# Story 20.2: Test Infrastructure Fixes

**Epic:** 20 — Hygiene & Quick Wins
**Status:** in-progress

## Story

As a **developer**,
I want **`tests/auth/__init__.py` to exist and all async test markers to use `@pytest.mark.asyncio`**,
so that **test discovery and async test execution follow standard pytest conventions**.

## Acceptance Criteria

- **Given** `tests/auth/` **When** I list files **Then** `__init__.py` exists.
- **Given** `pyproject.toml` **When** I inspect dev dependencies **Then** `pytest-asyncio` is listed.
- **Given** all test files **When** I search for `@pytest.mark.anyio` **Then** zero occurrences remain; all have been replaced with `@pytest.mark.asyncio`.
- **Given** the test suite **When** I run `uv run pytest` **Then** all tests pass.

## Tasks

- [x] Create `tests/auth/__init__.py`
- [x] Add `pytest-asyncio` to dev deps in `pyproject.toml`
- [x] Replace all `@pytest.mark.anyio` with `@pytest.mark.asyncio` across all test files
- [x] Configure `asyncio_mode` in `pyproject.toml`
