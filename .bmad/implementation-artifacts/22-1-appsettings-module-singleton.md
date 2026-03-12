# Story 22.1: AppSettings Module Singleton

## Status: in-progress

## Story

As a **developer**,
I want **a single `AppSettings` instance created once at module level and imported everywhere**,
so that **configuration is loaded once and there is a single source of truth at runtime**.

## Acceptance Criteria

- **Given** `core/config.py` **When** I inspect it **Then** a module-level instance (`settings = AppSettings()`) is defined after the class.
- **Given** all modules that previously called `AppSettings()` **When** I search the codebase **Then** zero call sites remain outside `core/config.py`; all import `settings` from `core.config`.
- **Given** tests that need to override settings **When** I inspect them **Then** they use monkeypatch, env var overrides, or dependency overrides — not `AppSettings()` construction.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Add `settings = AppSettings()` singleton to `core/config.py`
- [x] Update `main.py` to import and use the singleton
- [x] Update `api/v1/dummy_routes.py` to use the singleton
- [x] Update `api/v2/dummy_routes.py` to use the singleton
- [x] Update `auth/dependencies.py` to use the singleton
- [x] Update `services/v1/dummy_service.py` to use the singleton
- [x] Update `services/v2/dummy_service.py` to use the singleton
- [x] Update `core/database.py` to use the singleton as fallback
- [x] Update `tests/core/test_database.py` to use singleton / monkeypatch
