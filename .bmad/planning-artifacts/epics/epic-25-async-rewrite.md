# Epic 25: Async Rewrite

Convert the entire request → service → DB path to async. This is the most invasive epic and should be executed last, after all prior cleanup is in place (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 40–47).

## Context

The application currently uses synchronous route handlers, synchronous service functions, and synchronous SQLAlchemy sessions (`Session`, `sessionmaker`, `create_engine`). By this point in the execution order, the codebase is already using plain functions (Epic 24) and structlog (Epic 23), so the async conversion is a cleaner, more localized change.

SQLAlchemy's async engine requires async-compatible database drivers: `aiosqlite` for SQLite (dev/test) and `aiomysql` for MariaDB (production). These are new runtime dependencies.

## Problem Statement

- **Sync-only stack:** All route handlers and service functions are `def`, not `async def`; under uvicorn's ASGI server, synchronous handlers block the event loop or are dispatched to a thread pool, reducing throughput.
- **Sync DB sessions:** `Session` and `create_engine` are synchronous; switching to `AsyncSession` requires async drivers and dialect URL changes.
- **Test infrastructure:** Test fixtures use synchronous engine/session setup; async tests require `pytest-asyncio` fixtures and async engine creation.
- **AOP decorator:** `log_io` does not handle coroutines; wrapping an `async def` with a sync decorator loses the coroutine.
- **Scripts:** `scripts/build_template.py` and `scripts/remove_demo.py` reference the pre-async directory structure and patterns; they must be updated after all structural and async changes are complete.

## Proposed Epic Goal

1. Convert all route handlers and service functions to `async def`.
2. Add `aiosqlite` and `aiomysql` as runtime dependencies.
3. Switch to `AsyncSession`, `async_sessionmaker`, and `create_async_engine`; update dialect URLs.
4. Rewrite test fixtures for async engine/session.
5. Update the `log_io` AOP decorator to handle coroutines.
6. Add `nest_asyncio` to dev deps for async REPL.
7. Update `scripts/build_template.py` and `scripts/remove_demo.py` for the new structure.
8. Comprehensive `PROJECT_CONTEXT.md` update per the action 45 checklist.

## Success Criteria

- All route handlers and service functions are `async def`.
- `aiosqlite` and `aiomysql` are runtime dependencies in `pyproject.toml`.
- `core/database.py` uses `create_async_engine`, `AsyncSession`, and `async_sessionmaker`; dialect URLs use async drivers (e.g. `sqlite+aiosqlite://`, `mysql+aiomysql://`).
- Test fixtures use async engine/session; `pytest-asyncio` is in dev deps (added in Epic 20).
- `log_io` correctly wraps both sync and async functions.
- `nest_asyncio` (or `nest_asyncio2`) is in dev deps.
- `scripts/build_template.py` and `scripts/remove_demo.py` work correctly with the new codebase structure and async patterns.
- `PROJECT_CONTEXT.md` is updated per the action 45 checklist.
- All quality checks pass.

If the resulting PR is too large for comfortable review, this epic may be split into E25a (async routes + services) and E25b (async DB layer + test infrastructure).

## Stories

### Story 25.1: Async Routes and Service Functions

As a **developer**,
I want **all route handlers and service functions converted to `async def`**,
so that **the application fully leverages ASGI's async event loop**.

**Acceptance Criteria:**

- **Given** all route handler functions in `api/v1/` and `api/v2/` **When** I inspect them **Then** they are `async def`.
- **Given** all service functions in `services/v1/` and `services/v2/` (default and mock) **When** I inspect them **Then** they are `async def`.
- **Given** the application **When** started and requests are made **Then** routes execute asynchronously without blocking the event loop.
- **Given** the test suite **When** I run it **Then** route and service tests pass (test infrastructure updates may be needed; see Story 25.3).

### Story 25.2: Async Database Layer

As a **developer**,
I want **async DB drivers added and the database module switched to `create_async_engine`, `AsyncSession`, and `async_sessionmaker`**,
so that **database I/O is non-blocking and compatible with async service functions**.

**Acceptance Criteria:**

- **Given** `pyproject.toml` **When** I inspect runtime dependencies **Then** `aiosqlite` and `aiomysql` are listed.
- **Given** `core/database.py` **When** I inspect it **Then** it uses `create_async_engine` instead of `create_engine`, `async_sessionmaker` instead of `sessionmaker`, and `AsyncSession` instead of `Session`.
- **Given** `core/database.py` **When** SQLite is the effective database (no `DATABASE_URL`) **Then** the dialect URL is `sqlite+aiosqlite://` (not `sqlite://`).
- **Given** `core/database.py` **When** `DATABASE_URL` is set for MariaDB **Then** the dialect is `mysql+aiomysql://` (or the URL is remapped from `pymysql` to `aiomysql`).
- **Given** `get_session()` **When** I inspect it **Then** it yields `AsyncSession` instances (async generator).
- **Given** service functions **When** they use the session **Then** they `await` session operations (`await session.execute(...)`, `await session.commit()`, etc.).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 25.3: Async Test Infrastructure

As a **developer**,
I want **test fixtures rewritten for async engine/session creation**,
so that **tests can exercise async routes and services**.

**Acceptance Criteria:**

- **Given** `tests/conftest.py` **When** I inspect it **Then** the engine fixture uses `create_async_engine` with `sqlite+aiosqlite://` and `AsyncSession`.
- **Given** `tests/auth/conftest.py` **When** I inspect it **Then** async-compatible fixtures are used where needed.
- **Given** test files **When** I inspect async test functions **Then** they use `@pytest.mark.asyncio` (added in Epic 20) and `await` where appropriate.
- **Given** the full test suite **When** I run `uv run pytest` **Then** all tests pass.

### Story 25.4: Async-Aware AOP and Dev Tooling

As a **developer**,
I want **the `log_io` decorator to correctly handle coroutines and `nest_asyncio` available for async REPL**,
so that **AOP logging works with async functions and interactive debugging is possible**.

**Acceptance Criteria:**

- **Given** `aop/logging_decorator.py` **When** I inspect `log_io` **Then** it detects whether the wrapped function is a coroutine function (`asyncio.iscoroutinefunction`) **And** returns an async wrapper for coroutines and a sync wrapper for regular functions.
- **Given** an `async def` service function wrapped by `log_io` **When** it is called **Then** inputs are logged at DEBUG, the return value is logged at DEBUG, and exceptions are logged at ERROR — same behaviour as sync functions.
- **Given** `pyproject.toml` **When** I inspect dev dependencies **Then** `nest_asyncio` (or `nest_asyncio2`) is listed.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 25.5: Script Updates and PROJECT_CONTEXT for Async Rewrite

As a **developer or agent**,
I want **Cookiecutter and demo removal scripts updated for the new structure, and `PROJECT_CONTEXT.md` comprehensively updated for async patterns**,
so that **scaffolding tools work and documentation matches the async codebase**.

**Acceptance Criteria:**

- **Given** `scripts/build_template.py` **When** I run it **Then** it generates a project that reflects the current directory structure (flat `services/v*/`, no `contracts/` or `implementations/`, functional patterns, async throughout).
- **Given** `scripts/remove_demo.py` **When** I run it **Then** it correctly strips Dummy CRUD boilerplate from the current structure **And** all remaining tests pass.
- **Given** `PROJECT_CONTEXT.md` § Technology Stack **When** I read it **Then** `aiosqlite`, `aiomysql`, and `pytest-asyncio` are in the tables.
- **Given** `PROJECT_CONTEXT.md` § Data Persistence **When** I read it **Then** it documents `AsyncSession`, `async_sessionmaker`, and async `get_session`.
- **Given** `PROJECT_CONTEXT.md` § AOP Function Logging **When** I read it **Then** it documents the async-aware `log_io` decorator.
- **Given** `PROJECT_CONTEXT.md` § Testing **When** I read it **Then** it documents async fixtures and `pytest-asyncio` markers.
- **Given** `PROJECT_CONTEXT.md` § Code style **When** I read it **Then** it documents `async def` conventions.
- **Given** `PROJECT_CONTEXT.md` § Adding a New Resource recipe **When** I read it **Then** steps reference async service functions and async route handlers.
- **Given** `PROJECT_CONTEXT.md` § Anti-Patterns **When** I read it **Then** it includes guidance on sync vs async (e.g. "Do not use synchronous `def` for route handlers or service functions").
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.
