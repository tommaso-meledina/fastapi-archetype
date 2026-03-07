# Story 17.3: Documentation — DATABASE_URL, Default SQLite, and URL Escaping

Status: done

## Story

As a **developer or operator**,
I want **PROJECT_CONTEXT, .env.example, and README to describe database configuration via optional `DATABASE_URL` and default SQLite behaviour**,
so that **I know how to run with zero config (SQLite) or plug in any backend by setting the URL and installing the right driver**.

## Acceptance Criteria

1. **Given** PROJECT_CONTEXT **When** I read the Data Persistence / database section **Then** it describes optional `DATABASE_URL`, default SQLite when unset, URL used as-is when set, and note on escaping special characters.
2. **Given** `.env.example` **When** I read it **Then** the database section documents optional `DATABASE_URL` and the note about escaping special characters.
3. **Given** README **When** I read the run or database section **Then** it explains default SQLite when `DATABASE_URL` is not set and how to set `DATABASE_URL` for Compose or a server database.

## Tasks / Subtasks

- [x] Task 1 — PROJECT_CONTEXT Data Persistence: DATABASE_URL, default SQLite, escaping note.
- [x] Task 2 — .env.example: DATABASE_URL section and escaping note.
- [x] Task 3 — README: default SQLite and DATABASE_URL for Compose/server.

## Dev Agent Record

### File List

PROJECT_CONTEXT.md, .env.example, README.md
