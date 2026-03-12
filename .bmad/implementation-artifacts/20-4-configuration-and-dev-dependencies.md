# Story 20.4: Configuration and Dev Dependencies

**Epic:** 20 — Hygiene & Quick Wins
**Status:** in-progress

## Story

As a **developer**,
I want **`log_level` to use an `Enum` and `ipdb` available as a dev dependency**,
so that **config validation is type-safe and interactive debugging is readily available**.

## Acceptance Criteria

- **Given** `core/config.py` **When** I inspect `log_level` on `AppSettings` **Then** its type is an `Enum` (e.g. `LogLevel(str, Enum)` or `StrEnum`) with members for valid log levels **And** Pydantic validates against the enum at startup.
- **Given** `pyproject.toml` **When** I inspect dev dependencies **Then** `ipdb` is listed.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Introduce `LogLevel(StrEnum)` in `core/config.py` with DEBUG/INFO/WARNING/ERROR/CRITICAL members
- [x] Change `log_level` field type from `str` to `LogLevel`
- [x] Replace manual string validator with `mode="before"` normalizer that uppercases input
- [x] Remove `VALID_LOG_LEVELS` frozenset
- [x] Add `ipdb` to dev deps in `pyproject.toml`
- [x] Update `tests/core/test_config.py` where the error match string changed
