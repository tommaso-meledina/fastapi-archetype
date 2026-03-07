# Story 17.1: Config and Database Module — DATABASE_URL and Two Engine-Setup Functions

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **software engineer**,
I want **configuration to use an optional `DATABASE_URL` and the database module to expose a SQLite engine builder and a generic URL engine builder**,
so that **the app defaults to SQLite when no URL is set and uses any validated URL otherwise, with clear separation of SQLite vs other backends**.

## Acceptance Criteria

1. **Given** `core/config.py` **When** this story is complete **Then** `AppSettings` has no `db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, or `db_name` **And** it has an optional `database_url` (e.g. `str | None = None` or equivalent) such that when unset or empty/whitespace the effective URL is `sqlite://`.
2. **Given** `core/database.py` **When** I inspect it **Then** there is a function that creates an engine for SQLite (applying `StaticPool` and `check_same_thread=False`) **And** a function that creates an engine from a given URL for non-SQLite backends (no SQLite-specific kwargs).
3. **Given** the logic that chooses which engine to create **When** `DATABASE_URL` is not set or the effective URL starts with `sqlite://` **Then** the SQLite builder is used **When** `DATABASE_URL` is set and does not start with `sqlite://` **Then** the URL is validated (e.g. with `sqlalchemy.engine.make_url`) and the other builder is used; invalid URL raises at startup with a clear error.
4. **Given** the test suite **When** I run it **Then** no tests depend on `db_driver` or the removed DB_* fields (tests are updated in Story 17.4; this story may leave some tests temporarily skipped or failing until then, or tests may be updated in the same story—see project preference).

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — AppSettings: remove DB_* fields, add optional database_url
  - [x] Remove `db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, `db_name` from AppSettings.
  - [x] Add optional `database_url: str | None = None` (or equivalent); treat empty/whitespace as unset; effective URL when unset is `sqlite://`.
- [x] Task 2 (AC: #2) — core/database.py: two engine builders
  - [x] Add function that creates SQLite engine (StaticPool, check_same_thread=False).
  - [x] Add function that creates engine from a given URL for non-SQLite (no SQLite kwargs).
- [x] Task 3 (AC: #3) — Engine selection and validation
  - [x] When DATABASE_URL unset or effective URL starts with sqlite:// → use SQLite builder.
  - [x] When DATABASE_URL set and not sqlite:// → validate with sqlalchemy.engine.make_url, use generic URL builder; invalid URL raise at startup with clear error.
- [x] Task 4 (AC: #4) — Tests
  - [x] Update or skip tests that reference db_driver/DB_* as needed (full test update in 17.4).

## Dev Notes

- Epic 17: Database URL Configuration — single optional DATABASE_URL; default SQLite in-memory; two engine paths (SQLite vs generic URL).
- **Effective URL:** Empty or whitespace-only DATABASE_URL → treat as unset → `sqlite://`.
- **Validation:** Use `sqlalchemy.engine.make_url()`; on failure raise with clear message at startup.
- **Source:** [Epic 17](.bmad/planning-artifacts/epics/epic-17-database-url-configuration.md), [PROJECT_CONTEXT](PROJECT_CONTEXT.md).

### Project Structure Notes

- `core/config.py`: AppSettings only; no DB_*; optional database_url.
- `core/database.py`: get_engine(settings) chooses builder; two internal builders (SQLite, from URL).

### References

- [Source: .bmad/planning-artifacts/epics/epic-17-database-url-configuration.md]
- [Source: PROJECT_CONTEXT.md — Data Persistence]
- [Source: src/fastapi_archetype/core/config.py, core/database.py]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
