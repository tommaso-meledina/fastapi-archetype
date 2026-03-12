# Epic 22: Configuration & Module Organization

Introduce an `AppSettings` module singleton, add `__all__` exports to key packages, and add a task runner file for standard commands (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 17–20).

## Context

`AppSettings()` is currently instantiated at every call site, creating redundant Pydantic settings objects. Key `__init__.py` files lack `__all__`, making the public API of each package implicit. There is no single task runner file for common commands (lint, format, typecheck, test, run).

## Problem Statement

- **Repeated instantiation:** `AppSettings()` is called in ~10 modules; each call reads env vars and constructs a new object unnecessarily.
- **Implicit exports:** Without `__all__`, autocomplete and re-exports are unreliable; consumers import from internal modules rather than the package boundary.
- **No task runner:** Developers must remember individual tool commands; there is no `make lint` or `just test` shortcut.

## Proposed Epic Goal

1. Implement a module-level singleton for `AppSettings` in `core/config.py`.
2. Replace all `AppSettings()` call sites with the singleton import.
3. Add `__all__` to key `__init__.py` files.
4. Add a Justfile or Makefile with standard commands.

## Success Criteria

- `core/config.py` exports a module-level `settings` singleton.
- Zero occurrences of `AppSettings()` outside `core/config.py`.
- Key `__init__.py` files (~10 packages) define `__all__`.
- A `Justfile` or `Makefile` exists in the project root with at least `lint`, `format`, `typecheck`, `test`, and `run` targets.
- All quality checks pass.

## Stories

### Story 22.1: AppSettings Module Singleton

As a **developer**,
I want **a single `AppSettings` instance created once at module level and imported everywhere**,
so that **configuration is loaded once and there is a single source of truth at runtime**.

**Acceptance Criteria:**

- **Given** `core/config.py` **When** I inspect it **Then** a module-level instance (e.g. `settings = AppSettings()`) is defined after the class.
- **Given** all modules that previously called `AppSettings()` **When** I search the codebase **Then** zero call sites remain outside `core/config.py`; all import `settings` from `core.config` (or the appropriate package path).
- **Given** tests that need to override settings **When** I inspect them **Then** they use monkeypatch, env var overrides, or dependency overrides — not `AppSettings()` construction.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 22.2: Module Exports and Task Runner

As a **developer**,
I want **`__all__` defined in key `__init__.py` files and a task runner file in the project root**,
so that **package APIs are explicit and common commands are discoverable**.

**Acceptance Criteria:**

- **Given** key `__init__.py` files (at minimum: `api/v1/`, `api/v2/`, `auth/`, `core/`, `models/entities/`, `models/dto/v1/`, `factories/`, `observability/`, `services/`) **When** I inspect them **Then** each defines `__all__` listing the public symbols of the package.
- **Given** the project root **When** I list files **Then** a `Justfile` or `Makefile` exists.
- **Given** the task runner **When** I read it **Then** it defines at least: `lint` (`uv run ruff check`), `format` (`uv run ruff format --check`), `typecheck` (`uv run ty check`), `test` (`uv run pytest`), and `run` (uvicorn startup command).
- **Given** the test suite **When** I run all quality checks **Then** all pass.
