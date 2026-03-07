# Epic 17: Database URL Configuration

A developer configures the database via an optional `DATABASE_URL` environment variable; when unset, the application uses SQLite in-memory. When set, the URL is validated at startup and used as-is (the appropriate driver library must be in dependencies). Engine creation is split into a SQLite-specific path and a generic URL path, enabling plug-and-play with any SQLAlchemy-supported backend (PostgreSQL, Oracle, etc.) without code changes.

## Context

The application currently uses `DB_DRIVER` with `Literal["sqlite", "mysql+pymysql"]` and separate `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` to build a connection URL. This ties configuration to two concrete backends and does not scale to other databases (PostgreSQL, Oracle, etc.) without code changes.

## Problem Statement

- **Backend-specific configuration:** `DB_DRIVER=mysql+pymysql` and the built URL are MariaDB/MySQL-specific; adding PostgreSQL or Oracle would require new Literal values and URL-building logic.
- **Redundant env vars:** When using a server database, operators often prefer a single `DATABASE_URL` (12-factor style) rather than five separate variables.
- **No single “other” path:** There is no generic “use this URL” path; all non-SQLite behaviour is tied to one dialect.

## Proposed Epic Goal

1. **Drop `DB_DRIVER` and all `DB_*` connection fields** from `AppSettings` (`db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, `db_name`).
2. **Introduce optional `DATABASE_URL`:** If unset or empty/whitespace, the application defaults to SQLite in-memory (`sqlite://`). If set, the URL is used as-is after validation.
3. **Split engine creation into two functions in `core/database.py`:**
   - **SQLite path:** A function that creates an engine for SQLite (in-memory or file URL), applying `StaticPool` and `check_same_thread=False`.
   - **Other backends:** A function that creates an engine from a given URL (no SQLite-specific kwargs). Config/code invokes the SQLite path when `DATABASE_URL` is not set or when the effective URL starts with `sqlite://`; otherwise it validates the URL and invokes the other path.
4. **Validate `DATABASE_URL` at startup** when set (e.g. via `sqlalchemy.engine.make_url()`); fail fast with a clear error if invalid.
5. **Document behaviour:** PROJECT_CONTEXT, `.env.example`, and README explain optional `DATABASE_URL` and default SQLite. Document that special characters (e.g. `@`, `:`, `/`, `%`) in any component of `DATABASE_URL` must be escaped if used.
6. **Update Compose:** `compose/.env` and `compose/docker-compose.yaml` use a single `DATABASE_URL` (built from existing MariaDB-related vars) instead of `DB_DRIVER` and the five `DB_*` variables.

## Success Criteria

- No `DB_DRIVER` or `db_driver` in the codebase; no `db_host`, `db_port`, `db_user`, `db_password`, `db_name` in `AppSettings`.
- Optional `database_url` (or equivalent) on `AppSettings`; effective URL is `sqlite://` when unset or empty.
- Two clearly separated engine-creation functions: one for SQLite, one for any other URL (used after validation).
- Invalid `DATABASE_URL` causes startup failure with a clear message.
- Compose stack runs the app against MariaDB using only `DATABASE_URL` (or a single composed value).
- Docs describe `DATABASE_URL`, default behaviour, and that special characters in the URL must be escaped where applicable.
- All existing tests pass (adjusted for new config shape); new tests cover default SQLite, set URL, and validation failure.

## Stories

### Story 17.1: Config and Database Module — DATABASE_URL and Two Engine-Setup Functions

As a **software engineer**,
I want **configuration to use an optional `DATABASE_URL` and the database module to expose a SQLite engine builder and a generic URL engine builder**,
so that **the app defaults to SQLite when no URL is set and uses any validated URL otherwise, with clear separation of SQLite vs other backends**.

**Acceptance Criteria:**

- **Given** `core/config.py` **When** this story is complete **Then** `AppSettings` has no `db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, or `db_name` **And** it has an optional `database_url` (e.g. `str | None = None` or equivalent) such that when unset or empty/whitespace the effective URL is `sqlite://`.
- **Given** `core/database.py` **When** I inspect it **Then** there is a function that creates an engine for SQLite (applying `StaticPool` and `check_same_thread=False`) **And** a function that creates an engine from a given URL for non-SQLite backends (no SQLite-specific kwargs).
- **Given** the logic that chooses which engine to create **When** `DATABASE_URL` is not set or the effective URL starts with `sqlite://` **Then** the SQLite builder is used **When** `DATABASE_URL` is set and does not start with `sqlite://` **Then** the URL is validated (e.g. with `sqlalchemy.engine.make_url`) and the other builder is used; invalid URL raises at startup with a clear error.
- **Given** the test suite **When** I run it **Then** no tests depend on `db_driver` or the removed DB_* fields (tests are updated in Story 17.4; this story may leave some tests temporarily skipped or failing until then, or tests may be updated in the same story—see project preference).

### Story 17.2: Docker Compose and compose/.env — Use DATABASE_URL Only

As a **software engineer**,
I want **the Compose stack to pass a single `DATABASE_URL` to the application instead of `DB_DRIVER` and the five `DB_*` variables**,
so that **the app connects to MariaDB using 12-factor-style configuration and the compose env stays consistent with the new config model**.

**Acceptance Criteria:**

- **Given** `compose/docker-compose.yaml` **When** I inspect the `fastapi-archetype` service environment **Then** it does not set `DB_DRIVER`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, or `DB_NAME` **And** it sets `DATABASE_URL` to a full connection URL (e.g. built from `DATASOURCE_USER`, `DATASOURCE_PASSWORD`, `DATABASE_NAME`, and the MariaDB service host/port).
- **Given** `compose/.env` **When** I inspect it **Then** it does not define `DB_DRIVER`, `DB_HOST`, or `DB_PORT` **And** it retains `DATABASE_NAME`, `DATASOURCE_USER`, `DATASOURCE_PASSWORD` (or equivalent) for the MariaDB service and for building `DATABASE_URL` in the compose file if desired.
- **Given** the compose environment **When** I run `docker compose up` **Then** the application starts and connects to MariaDB successfully **And** `POST /dummies` and `GET /dummies` behave correctly against MariaDB.

### Story 17.3: Documentation — DATABASE_URL, Default SQLite, and URL Escaping

As a **developer or operator**,
I want **PROJECT_CONTEXT, .env.example, and README to describe database configuration via optional `DATABASE_URL` and default SQLite behaviour**,
so that **I know how to run with zero config (SQLite) or plug in any backend by setting the URL and installing the right driver**.

**Acceptance Criteria:**

- **Given** PROJECT_CONTEXT **When** I read the Data Persistence / database section **Then** it describes that database connection is configured by an optional `DATABASE_URL` **And** when unset, the app uses SQLite in-memory **And** when set, the URL is used as-is and the appropriate driver must be in dependencies **And** it notes that special characters (e.g. `@`, `:`, `/`, `%`) used within `DATABASE_URL` must be escaped.
- **Given** `.env.example` **When** I read it **Then** the database section documents optional `DATABASE_URL` (omit for SQLite in-memory; set for MariaDB/PostgreSQL/etc.) **And** includes the same note about escaping special characters in the URL where applicable.
- **Given** README **When** I read the run or database section **Then** it explains that the app defaults to SQLite when `DATABASE_URL` is not set **And** how to set `DATABASE_URL` for Compose or a server database (with reference to compose or `.env.example` as appropriate).

### Story 17.4: Tests — Config and Database for DATABASE_URL

As a **software engineer**,
I want **config and database tests updated to assert on `DATABASE_URL` behaviour (default SQLite, set URL, validation failure) and to stop using `db_driver` / DB_* **,
so that **the new configuration and engine-selection logic are covered and the suite passes**.

**Acceptance Criteria:**

- **Given** `tests/core/test_config.py` **When** this story is complete **Then** there are no tests that reference `db_driver`, `db_host`, `db_port`, `db_user`, `db_password`, or `db_name` **And** there are tests that: (1) default/empty `DATABASE_URL` yields effective URL `sqlite://` (or equivalent assertion), (2) when `DATABASE_URL` is set to a valid value, the effective URL is that value.
- **Given** `tests/core/test_database.py` **When** I run it **Then** engine creation uses the new config (e.g. `AppSettings()` with no `DATABASE_URL` for SQLite, or equivalent) **And** tests that previously used `AppSettings(db_driver="sqlite")` are updated accordingly.
- **Given** any test that validated `database_url` property for MySQL **When** this story is complete **Then** it is removed or replaced with a test that sets `DATABASE_URL` to a non-SQLite URL and asserts the effective URL or engine behaviour as appropriate.
- **Given** invalid `DATABASE_URL` **When** the app or config is loaded **Then** a test asserts that validation fails with a clear error (e.g. invalid URL format).
- **Given** the full test suite **When** I run it **Then** all tests pass.

## Notes

- **Driver dependencies:** The project keeps PyMySQL in dependencies for the default Compose (MariaDB). For PostgreSQL or Oracle, operators add the corresponding driver and set `DATABASE_URL`; no code change required.
- **Effective URL:** Treat empty or whitespace-only `DATABASE_URL` as “not set” so that the default remains SQLite.
- **Core architectural decisions:** The Data Architecture table and cascading implication in `core-architectural-decisions.md` should be updated to describe database configuration via optional `DATABASE_URL` instead of `DB_DRIVER` (can be done in Story 17.3 or in a small follow-up).
