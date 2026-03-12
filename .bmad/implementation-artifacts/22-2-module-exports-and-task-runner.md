# Story 22.2: Module Exports and Task Runner

## Status: in-progress

## Story

As a **developer**,
I want **`__all__` defined in key `__init__.py` files and a task runner file in the project root**,
so that **package APIs are explicit and common commands are discoverable**.

## Acceptance Criteria

- **Given** key `__init__.py` files (at minimum: `api/v1/`, `api/v2/`, `auth/`, `core/`, `models/entities/`, `models/dto/v1/`, `factories/`, `observability/`, `services/`) **When** I inspect them **Then** each defines `__all__` listing the public symbols of the package.
- **Given** the project root **When** I list files **Then** a `Justfile` or `Makefile` exists.
- **Given** the task runner **When** I read it **Then** it defines at least: `lint` (`uv run ruff check`), `format` (`uv run ruff format --check`), `typecheck` (`uv run ty check`), `test` (`uv run pytest`), and `run` (uvicorn startup command).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Add `__all__` to `api/v1/__init__.py`
- [x] Add `__all__` to `api/v2/__init__.py`
- [x] Add `__all__` to `auth/__init__.py`
- [x] Add `__all__` to `core/__init__.py`
- [x] Add `__all__` to `models/entities/__init__.py`
- [x] Add `__all__` to `models/dto/v1/__init__.py`
- [x] Add `__all__` to `factories/__init__.py`
- [x] Add `__all__` to `observability/__init__.py`
- [x] Add `__all__` to `services/__init__.py`
- [x] Create `Justfile` in project root
