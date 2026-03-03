# Story 1.1: Project Initialization and Package Structure

Status: done

## Story

As a **software engineer**,
I want **a cleanly initialized Python 3.14 / FastAPI project with a fully defined package structure and linting configuration**,
so that **I have a runnable project skeleton where every module has a clear home and code style is enforced from the start**.

## Acceptance Criteria

1. `pyproject.toml` exists with `requires-python = ">=3.14"`, project name `fastapi-archetype`, and FastAPI + Uvicorn as dependencies; `.python-version` is pinned to `3.14`; `uv.lock` is generated.
2. `src/fastapi_archetype/` package exists with `__init__.py`; subpackages `core/`, `models/`, `api/`, `services/`, `aop/`, `observability/` each with `__init__.py`.
3. `tests/` directory exists at project root with `__init__.py`.
4. `src/fastapi_archetype/main.py` exists; running with `uv run uvicorn fastapi_archetype.main:app` starts FastAPI; Swagger UI at `/docs`.
5. Ruff is configured in `pyproject.toml`; `uv run ruff check` and `uv run ruff format --check` pass with zero violations.
6. `.gitignore` exists with appropriate Python/uv exclusions; no dead code, commented-out blocks, or placeholder implementations.

## Tasks / Subtasks

- [x] Task 1: Initialize project with uv (AC: 1)
  - [x] Run `uv init` with appropriate settings for src layout
  - [x] Set `requires-python = ">=3.14"` in pyproject.toml
  - [x] Pin `.python-version` to `3.14`
  - [x] Add FastAPI and Uvicorn as dependencies via `uv add`
  - [x] Generate `uv.lock`
- [x] Task 2: Create package structure (AC: 2, 3)
  - [x] Create `src/fastapi_archetype/__init__.py`
  - [x] Create subpackages: `core/`, `models/`, `api/`, `services/`, `aop/`, `observability/` each with `__init__.py`
  - [x] Create `tests/__init__.py` at project root
- [x] Task 3: Create FastAPI application entry point (AC: 4)
  - [x] Create `src/fastapi_archetype/main.py` with FastAPI app instance
  - [x] Ensure `/docs` serves Swagger UI
  - [x] Verify app starts with `uv run uvicorn fastapi_archetype.main:app`
- [x] Task 4: Configure Ruff linting and formatting (AC: 5)
  - [x] Add Ruff as dev dependency
  - [x] Configure Ruff in `pyproject.toml` with appropriate rules
  - [x] Verify `uv run ruff check` passes
  - [x] Verify `uv run ruff format --check` passes
- [x] Task 5: Create .gitignore and cleanup (AC: 6)
  - [x] Create `.gitignore` with Python/uv exclusions
  - [x] Remove any dead code or placeholder implementations
  - [x] Final verification of all ACs

## Dev Notes

- **Project uses src layout**: `src/fastapi_archetype/` per Python Packaging User Guide
- **uv** is the dependency manager — use `uv init`, `uv add`, `uv run`
- **Python 3.14** is required — pin in both `pyproject.toml` and `.python-version`
- **Ruff v0.15.4** specified in architecture — single tool replacing flake8 + black + isort
- **FastAPI** is the framework; **Uvicorn 0.41.0** is the ASGI server
- **Empty `__init__.py` files** are fine for subpackages at this stage
- **No tests needed in this story** — test infrastructure is Epic 4
- **Startup sequence**: Config validation → DB engine → Middleware → Routes (but in this story just the basic app)

### Project Structure Notes

Target structure from architecture:
```
fastapi-archetype/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── src/
│   └── fastapi_archetype/
│       ├── __init__.py
│       ├── main.py
│       ├── core/
│       │   └── __init__.py
│       ├── models/
│       │   └── __init__.py
│       ├── api/
│       │   └── __init__.py
│       ├── services/
│       │   └── __init__.py
│       ├── aop/
│       │   └── __init__.py
│       └── observability/
│           └── __init__.py
└── tests/
    └── __init__.py
```

### References

- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md]
- [Source: .bmad/planning-artifacts/epics/epic-1-running-application-with-crud-api.md#Story 1.1]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Project initialized with `uv init --lib --package` for src layout
- FastAPI 0.135.1 + Uvicorn 0.41.0 added as dependencies
- Ruff 0.15.4 configured with E, W, F, I, N, UP, B, SIM, TCH rules
- All subpackages created with empty `__init__.py` files
- App verified: imports correctly, /docs /redoc /openapi.json routes present
- All Ruff checks pass with zero violations

### File List

- pyproject.toml (new)
- uv.lock (new)
- .python-version (new)
- .gitignore (new)
- src/fastapi_archetype/__init__.py (new)
- src/fastapi_archetype/main.py (new)
- src/fastapi_archetype/core/__init__.py (new)
- src/fastapi_archetype/models/__init__.py (new)
- src/fastapi_archetype/api/__init__.py (new)
- src/fastapi_archetype/services/__init__.py (new)
- src/fastapi_archetype/aop/__init__.py (new)
- src/fastapi_archetype/observability/__init__.py (new)
- tests/__init__.py (new)
