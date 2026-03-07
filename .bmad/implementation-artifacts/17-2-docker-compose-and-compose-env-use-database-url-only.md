# Story 17.2: Docker Compose and compose/.env — Use DATABASE_URL Only

Status: done

## Story

As a **software engineer**,
I want **the Compose stack to pass a single `DATABASE_URL` to the application instead of `DB_DRIVER` and the five `DB_*` variables**,
so that **the app connects to MariaDB using 12-factor-style configuration and the compose env stays consistent with the new config model**.

## Acceptance Criteria

1. **Given** `compose/docker-compose.yaml` **When** I inspect the `fastapi-archetype` service environment **Then** it does not set `DB_DRIVER`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, or `DB_NAME` **And** it sets `DATABASE_URL` to a full connection URL (e.g. built from `DATASOURCE_USER`, `DATASOURCE_PASSWORD`, `DATABASE_NAME`, and the MariaDB service host/port).
2. **Given** `compose/.env` **When** I inspect it **Then** it does not define `DB_DRIVER`, `DB_HOST`, or `DB_PORT` **And** it retains `DATABASE_NAME`, `DATASOURCE_USER`, `DATASOURCE_PASSWORD` (or equivalent) for the MariaDB service and for building `DATABASE_URL` in the compose file if desired.
3. **Given** the compose environment **When** I run `docker compose up` **Then** the application starts and connects to MariaDB successfully **And** `POST /dummies` and `GET /dummies` behave correctly against MariaDB.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — docker-compose.yaml: DATABASE_URL only for app
  - [x] Remove DB_DRIVER, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME from fastapi-archetype service.
  - [x] Set DATABASE_URL to mysql+pymysql://${DATASOURCE_USER}:${DATASOURCE_PASSWORD}@mariadb:3306/${DATABASE_NAME}.
- [x] Task 2 (AC: #2) — compose/.env: remove DB_* vars
  - [x] Remove DB_DRIVER, DB_HOST, DB_PORT from .env; keep DATABASE_NAME, DATASOURCE_USER, DATASOURCE_PASSWORD.
- [x] Task 3 (AC: #3) — Verify compose (manual or note)
  - [x] Document that user can run docker compose up to verify.

## Dev Notes

- Epic 17.2; app now reads only DATABASE_URL (Story 17.1).
- Source: [Epic 17](.bmad/planning-artifacts/epics/epic-17-database-url-configuration.md).

## Dev Agent Record

### File List
