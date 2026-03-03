# Story 4.1: Test Infrastructure and Configuration

Status: review

## Story

As a **software engineer**,
I want **a pytest test infrastructure with SQLite in-memory database override and shared fixtures**,
so that **tests run without external dependencies and I have a clear pattern for writing new tests against any resource**.

## Acceptance Criteria

1. `tests/conftest.py` exists and creates a SQLite in-memory SQLAlchemy engine, overrides the application's database session dependency with the SQLite session, provides a FastAPI `TestClient` fixture, and calls `SQLModel.metadata.create_all` against the test engine to set up tables.
2. `uv run pytest` discovers and executes tests from the `tests/` directory with no external infrastructure required (no MariaDB, no OTEL collector).
3. Each test function that requests the test client fixture gets an isolated database state, with the application's dependency injection overridden to use the SQLite test database.
4. pytest is configured in `pyproject.toml` with `testpaths`, `pythonpath`, and `addopts` including `--strict-markers`.

## Tasks / Subtasks

- [x] Task 1: Add test dependencies to `pyproject.toml` (AC: 2)
  - [x] Add `pytest>=8.0` to `[dependency-groups] dev`
  - [x] Add `pytest-cov>=6.0` to `[dependency-groups] dev`
  - [x] Note: `httpx>=0.28.1` already present in dev dependencies (required by `TestClient`)
  - [x] Add `[tool.pytest.ini_options]` section with `testpaths = ["tests"]`, `pythonpath = ["src"]`, `addopts = "--strict-markers -ra"`
  - [x] Run `uv sync` to update lockfile
- [x] Task 2: Create test directory structure (AC: 1, 3)
  - [x] Create `tests/__init__.py` (empty)
  - [x] Create `tests/api/__init__.py` (empty)
  - [x] Create `tests/services/__init__.py` (empty)
  - [x] Create `tests/core/__init__.py` (empty)
  - [x] Create `tests/aop/__init__.py` (empty)
- [x] Task 3: Implement `tests/conftest.py` (AC: 1, 3)
  - [x] Create SQLite in-memory engine with `StaticPool` and `check_same_thread=False`
  - [x] Call `SQLModel.metadata.create_all(engine)` to create test tables
  - [x] Create a `session` fixture yielding a `Session` bound to the test engine, wrapped in a transaction that rolls back after each test for isolation
  - [x] Create a `client` fixture that overrides `get_session` dependency with the test session, then yields a `TestClient(app)`
  - [x] Import `app` from `fastapi_archetype.main` and `get_session` from `fastapi_archetype.core.database`
- [x] Task 4: Add a smoke test to verify infrastructure (AC: 2, 3)
  - [x] Create `tests/api/test_dummy_routes.py` with a single `test_list_dummies_empty` test calling `GET /dummies` and asserting 200 + empty list
  - [x] Run `uv run pytest -v` to confirm discovery and execution
- [x] Task 5: Run quality checks
  - [x] `uv run ruff check src/ tests/` — lint passes
  - [x] `uv run ruff format --check src/ tests/` — format passes

## Dev Notes

### Critical Implementation Details

**Database module singleton issue:** `database.py` uses a module-level `_engine` singleton. Tests MUST NOT call `get_engine()` or trigger the production engine. Instead, tests create their own engine and override `get_session` via FastAPI dependency overrides. The `_engine` global is never touched.

**TestClient requires httpx:** FastAPI's `TestClient` wraps `httpx`. It's already in dev dependencies (`httpx>=0.28.1`).

**Session isolation pattern:** Each test must get a clean database state. The recommended pattern:

```python
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
import pytest

from fastapi_archetype.main import app
from fastapi_archetype.core.database import get_session

@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def _override():
        yield session
    app.dependency_overrides[get_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Key points:**
- Engine is `scope="session"` (created once per test run) — tables are created once
- Session fixture creates a fresh `Session` per test, then drops/recreates all tables after each test for isolation
- Client fixture overrides `get_session` so all route handlers use the test session
- `app.dependency_overrides.clear()` in teardown prevents cross-test contamination

### Observability in tests

The `lifespan` in `main.py` calls `setup_otel(app, settings)` and `setup_prometheus(app)`. When `TestClient` starts the app, lifespan runs. Since `OTEL_EXPORT_ENABLED` defaults to `False`, OTEL exports are no-ops. Prometheus instrumentator attaches middleware but doesn't require external services. No mocking needed for basic test infrastructure.

### pyproject.toml pytest configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "--strict-markers -ra"
```

- `pythonpath = ["src"]` ensures `import fastapi_archetype` works in tests
- `--strict-markers` catches typos in marker names
- `-ra` shows summary of all non-passing tests

### Architecture Compliance

- Test location: `tests/` at project root, mirroring source structure [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Test Organization]
- Shared fixtures in `tests/conftest.py` [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Complete Project Directory Structure]
- Database override via `Depends()` pattern [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Data Architecture]
- FR14: Integration tests run against in-memory SQLite, no external infrastructure [Source: .bmad/planning-artifacts/prd/functional-requirements.md#Testing]

### Anti-Patterns to Avoid

- Do NOT import or call `get_engine()` from tests — it triggers the production singleton
- Do NOT create a separate test `main.py` or test app — use the real `app` with dependency overrides
- Do NOT use `scope="function"` for the engine fixture — recreating engines per test is wasteful
- Do NOT leave `app.dependency_overrides` populated between tests — always clear in teardown
- Do NOT add `conftest.py` inside subdirectories yet — a single root `conftest.py` is sufficient for Story 4.1

### Previous Story Learnings (Story 3.2)

- `setup_prometheus(app)` is called at module level in `main.py` (after `app` creation), not in lifespan — because `Instrumentator.instrument()` calls `add_middleware()` which raises `RuntimeError` after app startup
- The lifespan creates `AppSettings()` which reads `.env` — tests will use defaults (no `.env` needed)
- `_engine` in `database.py` is a global singleton — be careful not to trigger it in test imports

### References

- [Source: .bmad/planning-artifacts/epics/epic-4-comprehensive-test-suite.md#Story 4.1]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR13, FR14]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Test Organization]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Complete Project Directory Structure]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Data Architecture]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added pytest>=8.0 and pytest-cov>=6.0 to dev dependencies in pyproject.toml
- Configured [tool.pytest.ini_options] with testpaths, pythonpath, and addopts
- Created test directory structure: tests/, tests/api/, tests/services/, tests/core/, tests/aop/ (all with __init__.py)
- Implemented tests/conftest.py with session-scoped engine fixture, per-test session fixture with drop/create isolation, and client fixture with dependency override
- Added smoke test test_list_dummies_empty verifying GET /dummies returns 200 + empty list
- All ruff lint + format checks pass; pytest discovers and executes 1 test successfully

### Change Log

- 2026-03-03: Implemented test infrastructure and configuration (Story 4.1) — pytest setup, SQLite test fixtures, smoke test

### File List

- pyproject.toml (modified)
- uv.lock (modified)
- tests/__init__.py (created)
- tests/conftest.py (created)
- tests/api/__init__.py (created)
- tests/api/test_dummy_routes.py (created)
- tests/services/__init__.py (created)
- tests/core/__init__.py (created)
- tests/aop/__init__.py (created)
