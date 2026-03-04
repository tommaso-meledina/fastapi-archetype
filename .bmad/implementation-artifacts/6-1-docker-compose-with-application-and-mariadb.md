# Story 6.1: Docker Compose with Application and MariaDB

Status: review

## Story

As a **software engineer**,
I want **a Docker Compose configuration that starts the application alongside a MariaDB instance with automatic database provisioning**,
so that **I can exercise the full application against a real database with a single command, matching the production database engine**.

## Acceptance Criteria

1. **Given** the compose file exists in the `./compose/` directory **When** I inspect its contents **Then** it defines at least two services: the application and MariaDB **And** the application service builds from the existing `Dockerfile` **And** the MariaDB service uses the official `mariadb` image.

2. **Given** the compose environment **When** I run `docker compose up` **Then** MariaDB starts and creates the application database automatically via MariaDB's Docker entrypoint environment variables **And** the application starts after MariaDB is healthy **And** the application connects to MariaDB using `DB_DRIVER=mysql+pymysql`.

3. **Given** the compose environment is running **When** I send `POST /dummies` followed by `GET /dummies` **Then** data is persisted in MariaDB and returned correctly.

4. **Given** the compose environment **When** I run `docker compose down` followed by `docker compose up` **Then** MariaDB data persists across restarts via a Docker volume.

5. **Given** the compose environment **When** I inspect the service configuration **Then** the application's database connection settings (host, port, user, password, database name) are configured through environment variables or an env file appropriate for the compose network **And** the MariaDB service has a health check that the application service depends on.

## Tasks / Subtasks

- [x] Task 1: Create `compose/.env` file with compose-specific environment variables (AC: 2, 5)
  - [x] Define `DATABASE_NAME`, `DATASOURCE_USER`, `DATASOURCE_PASSWORD` for MariaDB
  - [x] Define `DB_DRIVER=mysql+pymysql`, `DB_HOST=mariadb`, `DB_PORT=3306`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` for the application
  - [x] Define `FASTAPI_ARCHETYPE_CONTEXT_PATH` and `FASTAPI_ARCHETYPE_DOCKERFILE_PATH` for the build context
- [x] Task 2: Refine `compose/docker-compose.yaml` MariaDB service (AC: 1, 2, 4, 5)
  - [x] Ensure MariaDB uses `mariadb:11` image
  - [x] Configure health check using `healthcheck.sh --connect --innodb_initialized`
  - [x] Configure named volumes for data persistence
  - [x] Environment variables reference the `.env` file
- [x] Task 3: Refine `compose/docker-compose.yaml` application service (AC: 1, 2, 5)
  - [x] Build context points to project root using `FASTAPI_ARCHETYPE_CONTEXT_PATH`
  - [x] Dockerfile path references the existing `Dockerfile`
  - [x] Pass database connection environment variables (`DB_DRIVER`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`)
  - [x] `depends_on` with `condition: service_healthy` for MariaDB
- [x] Task 4: Run quality checks
  - [x] `uv run ruff check src/ tests/` passes
  - [x] `uv run ruff format --check src/ tests/` passes
  - [x] `uv run pytest` — 40 tests pass, no regressions

## Dev Notes

### Architecture Compliance

- Database (prod): MariaDB — PRD-specified [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Data Architecture]
- MariaDB driver: PyMySQL 1.1.2 — pure Python, `DB_DRIVER=mysql+pymysql` [Source: same]
- Configuration: pydantic-settings `BaseSettings` reads from environment variables; `env_file=".env"` in `SettingsConfigDict` — but in Docker, environment variables from compose override [Source: src/fastapi_archetype/core/config.py]
- Session management: FastAPI `Depends()` with generator [Source: src/fastapi_archetype/core/database.py]

### Existing Foundation

The `compose/docker-compose.yaml` already defines:
- `mariadb` service (image: `mariadb:11`, health check, volumes, network)
- `fastapi-archetype` service (build from Dockerfile, health check, `depends_on: mariadb`, network)
- `grafana`, `jaeger-all-in-one`, `otel-collector`, `prometheus` services (Story 6.2 scope)
- Named volumes: `mariadb-etc`, `mariadb-data`
- Network: `fastapi-archetype-poc`

The existing compose file uses `${VARIABLE}` syntax referencing env vars that don't exist in any `.env` file under `compose/`. A `compose/.env` file must be created.

### Key Configuration Mapping

The application's `AppSettings` in `config.py` reads these env vars:
- `DB_DRIVER` — must be `mysql+pymysql` for MariaDB
- `DB_HOST` — must be `mariadb` (the compose service name)
- `DB_PORT` — `3306`
- `DB_USER` — must match `MARIADB_USER` in the MariaDB service
- `DB_PASSWORD` — must match `MARIADB_PASSWORD` in the MariaDB service
- `DB_NAME` — must match `MARIADB_DATABASE` in the MariaDB service

The `database_url` property constructs: `mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}`

### Docker Build Context

The Dockerfile is at the project root. The compose file is in `./compose/`. Therefore:
- `FASTAPI_ARCHETYPE_CONTEXT_PATH` should be `..` (relative to compose directory)
- `FASTAPI_ARCHETYPE_DOCKERFILE_PATH` should be `Dockerfile` (at project root, which is the context)

### Previous Story Intelligence

- Story 5.1: Created multi-stage Dockerfile. Build stage uses `python:3.14-slim` + uv (0.10.7). Runtime uses non-root `app` user. CMD: `uvicorn fastapi_archetype.main:app --host 0.0.0.0 --port 8000`.
- Dockerfile does NOT copy `.env` — environment variables must be injected via Docker/Compose.
- `.dockerignore` excludes `.env`, `.bmad/`, `_bmad/`, `tests/`, `.cursor/`.
- All 38 tests pass, lint and format checks clean.

### References

- [Source: .bmad/planning-artifacts/epics/epic-6-docker-compose-infrastructure.md#Story 6.1]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Data Architecture]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Infrastructure & Deployment]
- [Source: src/fastapi_archetype/core/config.py]
- [Source: src/fastapi_archetype/core/database.py]
- [Source: compose/docker-compose.yaml]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Created `compose/.env` with MariaDB and application environment variables, build context paths, and OTEL collector configuration
- Refined `compose/docker-compose.yaml`: cleaned up deprecated `version` key, consolidated MariaDB volume to single `mariadb-data`, passed all DB connection env vars to application service, renamed network to `fastapi-archetype-net`, removed `${OTELCOL_ARGS}` from otel-collector command
- Added `.gitignore` exception for `compose/.env` so development compose configuration is tracked in git
- All 40 existing tests pass, lint and format checks clean

### Change Log

- 2026-03-04: Implemented Docker Compose with Application and MariaDB (Story 6.1)

### File List

- compose/.env (created)
- compose/docker-compose.yaml (modified)
- .gitignore (modified — added `!compose/.env` exception)
