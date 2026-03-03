# Story 1.6: Configurable Database Driver with SQLite Default

Status: done

## Story

As a **software engineer**,
I want **the application to default to SQLite in-memory when no database driver is configured**,
so that **I can clone the project, run it immediately without standing up MariaDB, and still exercise the full request-response cycle**.

## Acceptance Criteria

1. `core/config.py` defines `db_driver` with `Literal["sqlite", "mysql+pymysql"]` defaulting to `"sqlite"`; without `DB_DRIVER` set, the app starts using SQLite in-memory.
2. Setting `DB_DRIVER=mysql+pymysql` connects to MariaDB using the remaining `db_*` settings.
3. With the SQLite driver, `GET /dummies` and `POST /dummies` work correctly; data persists for the process lifetime.
4. `core/database.py` uses `StaticPool` and `check_same_thread=False` when the driver is `sqlite`.
5. `.env.example` documents `DB_DRIVER` options.

## Tasks / Subtasks

- [x] Task 1: Add `db_driver` setting to AppSettings (AC: 1, 2)
  - [x] Add `db_driver` field with Literal type and sqlite default
  - [x] Branch `database_url` property on driver value
- [x] Task 2: Update engine creation for SQLite compatibility (AC: 4)
  - [x] Pass `StaticPool` and `check_same_thread=False` when sqlite
- [x] Task 3: Update documentation (AC: 5)
  - [x] Update `.env.example` with `DB_DRIVER` documentation
  - [x] Update `README.md` with zero-setup run instructions
- [x] Task 4: Verify full request cycle (AC: 3)
  - [x] Smoke test GET and POST /dummies with SQLite driver

## Dev Notes

- `StaticPool` is required for in-memory SQLite so all requests share the same connection (and thus the same database)
- `check_same_thread=False` is needed because FastAPI runs sync endpoints in a thread pool
- This is a developer-experience feature; production deployments should set `DB_DRIVER=mysql+pymysql`

### References

- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR5a]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Data Architecture]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Completion Notes List

- Added `db_driver` Literal field to AppSettings defaulting to "sqlite"
- `database_url` property returns `sqlite://` for sqlite driver, mysql+pymysql URL otherwise
- Engine creation branches on driver to add StaticPool and check_same_thread
- `.env.example` and README updated with driver documentation
- Full smoke test passed: GET returns [], POST returns 201, GET returns created record

### File List

- src/fastapi_archetype/core/config.py (modified)
- src/fastapi_archetype/core/database.py (modified)
- .env.example (modified)
- README.md (modified)
