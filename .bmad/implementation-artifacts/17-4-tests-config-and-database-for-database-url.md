# Story 17.4: Tests — Config and Database for DATABASE_URL

Status: done

## Story

As a **software engineer**,
I want **config and database tests updated to assert on `DATABASE_URL` behaviour (default SQLite, set URL, validation failure) and to stop using `db_driver` / DB_*** ,
so that **the new configuration and engine-selection logic are covered and the suite passes**.

## Acceptance Criteria

1. **Given** `tests/core/test_config.py` **When** this story is complete **Then** no tests reference `db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, or `db_name` **And** tests for default/empty → `sqlite://`, set valid URL → that value.
2. **Given** `tests/core/test_database.py` **When** I run it **Then** engine creation uses the new config (e.g. `AppSettings()` for SQLite) **And** tests updated from `AppSettings(db_driver="sqlite")`.
3. **Given** invalid `DATABASE_URL` **When** the app or config is loaded **Then** a test asserts that validation fails with a clear error.
4. **Given** the full test suite **When** I run it **Then** all tests pass.

## Tasks / Subtasks

- [x] Task 1 — test_config.py: no DB_* references; tests for effective_database_url (default, empty, whitespace, set).
- [x] Task 2 — test_database.py: use AppSettings(); invalid URL test.
- [x] Task 3 — Full test suite passes.

## Dev Agent Record

Completed in Story 17-1 (config and database implementation included test updates).

### File List

tests/core/test_config.py, tests/core/test_database.py
