# Story 15.1: Add Entity and Versioned DTO Structure

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **software engineer**,
I want **entity models under `models/entities/` and web DTOs under `models/dto/v1/` (and later `v2/`)**,
so that **persistence and API contracts can evolve independently and version-specific shapes have a clear place**.

## Acceptance Criteria

1. **Given** the codebase **When** this story is complete **Then** `models/entities/dummy.py` exists with the Dummy SQLModel (table=True, same schema as today) **And** `models/dto/v1/dummy.py` exists with DTO class(es) for request/response with the same camelCase behaviour as the current API.
2. **Given** the new layout **When** I inspect the project **Then** the existing `models/dummy.py` is unchanged and still used by services and routes (no behavioural change yet).
3. **Given** the test suite **When** I run it **Then** all tests still pass.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Add entity and DTO modules without changing behaviour
  - [x] Create `src/fastapi_archetype/models/entities/` package (`__init__.py` if needed).
  - [x] Create `models/entities/dummy.py` with `Dummy` SQLModel (`table=True`), same schema as current `models/dummy.py`: `id`, `name`, `description`; same `__tablename__ = "DUMMY"` and table definition.
  - [x] Create `src/fastapi_archetype/models/dto/` and `models/dto/v1/` packages.
  - [x] Create `models/dto/v1/dummy.py` with Pydantic DTO(s) for request/response: same fields and camelCase via `alias_generator=_to_camel`, `populate_by_name=True` (match current API shape).
- [x] Task 2 (AC: #2, #3) — Leave existing model in place
  - [x] Do not change `models/dummy.py`; do not change any imports in routes, services, or tests. All existing code continues to use `models.dummy.Dummy`.
  - [x] Run full test suite and ensure all tests pass.

## Dev Notes

- Epic 15 goal: separate entity (ORM) from DTO (API); this story only adds the new structure; wiring and removal of legacy model happen in later stories.
- **Entity:** Copy of current `Dummy` into `models/entities/dummy.py` — SQLModel with `table=True`, same `__tablename__`, same fields. Used only for persistence; not used in routes yet.
- **DTO:** Plain Pydantic models (no `table=True`) in `models/dto/v1/dummy.py`. Must produce identical JSON shape to current API (camelCase). Typically one model for response (with `id`) and one for create request (e.g. `name`, `description` without `id`) if needed; can mirror current usage in routes.
- **No new dependencies:** PROJECT_CONTEXT and epic forbid new libraries; use only Pydantic/SQLModel already in stack.
- **Source:** [Epic 15](.bmad/planning-artifacts/epics/epic-15-separate-entity-dto-and-factories.md), [PROJECT_CONTEXT](PROJECT_CONTEXT.md), [models/dummy.py](src/fastapi_archetype/models/dummy.py).

### Project Structure Notes

- Current: single `models/dummy.py`. After this story: `models/entities/dummy.py` (entity), `models/dto/v1/dummy.py` (DTOs), and `models/dummy.py` unchanged.
- Directory name is `models/dto` (singular), not `dtos`.
- One model per file convention: one file per entity in `models/entities/`, one file per resource in `models/dto/v1/`.

### References

- [Source: .bmad/planning-artifacts/epics/epic-15-separate-entity-dto-and-factories.md] — Target structure, mapping approach, success criteria.
- [Source: PROJECT_CONTEXT.md — Data Persistence, REST API] — Current single-model and camelCase behaviour.
- [Source: src/fastapi_archetype/models/dummy.py] — Current Dummy schema to replicate in entity and DTO.

## Dev Agent Record

### Agent Model Used

-

### Debug Log References

### Completion Notes List

- Added `models/entities/` with Dummy SQLModel (table=True) matching current schema. Added `models/dto/v1/` with DummyCreate and DummyResponse Pydantic models with same camelCase behaviour. Left `models/dummy.py` and all route/service imports unchanged. All 168 tests pass; ruff clean.

### File List

- src/fastapi_archetype/models/entities/__init__.py (new)
- src/fastapi_archetype/models/entities/dummy.py (new)
- src/fastapi_archetype/models/dto/__init__.py (new)
- src/fastapi_archetype/models/dto/v1/__init__.py (new)
- src/fastapi_archetype/models/dto/v1/dummy.py (new)
