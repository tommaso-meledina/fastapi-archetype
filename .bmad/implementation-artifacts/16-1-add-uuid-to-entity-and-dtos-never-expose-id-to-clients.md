# Story 16.1: Add UUID to Entity and DTOs; Never Expose ID to Clients

Status: done

## Story

As a **software engineer**,
I want **the Dummy entity to have a `uuid` (string) and all Dummy DTOs to expose `uuid` and never expose internal `id`**,
so that **clients have a stable, opaque identifier and never see persistence IDs**.

## Acceptance Criteria

1. **Given** the Dummy entity **When** I inspect it **Then** it has a `uuid` property (string, UUID format) in addition to its existing fields **And** existing rows have UUIDs (migration or seed as needed).
2. **Given** any Dummy response DTO (list or single) **When** the API returns data **Then** the response includes `uuid` **And** does not include `id`.
3. **Given** the test suite **When** I run it **Then** tests verify that Dummy responses contain `uuid` and do not contain `id` where applicable.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Add uuid to Dummy entity and ensure existing data has UUIDs
  - [x] Add `uuid: str` (UUID format) to `models/entities/dummy.py` on the Dummy class; ensure unique and indexed for lookups.
  - [x] Ensure schema/seed or startup logic assigns UUIDs to existing rows (e.g. in lifespan or a one-off seed) so all Dummy rows have a uuid.
- [x] Task 2 (AC: #2) — DTOs expose uuid and never id
  - [x] Add `uuid: str` to `GetDummiesResponse`, `PostDummiesResponse` in `models/dto/v1/dummy.py`.
  - [x] Remove `id` from `PostDummiesResponse` (and any other DTO that currently exposes it).
  - [x] Update `factories/dummy.py`: `entity_to_get_response` and `entity_to_post_response` must set `uuid` from entity and must not pass `id` to response DTOs.
- [x] Task 3 (AC: #3) — Tests for uuid in responses and absence of id
  - [x] Add/update tests in `tests/api/test_dummy_routes.py` and `tests/api/test_v2_dummy_routes.py`: assert response bodies include `uuid` and do not include `id`.
  - [x] Add/update service tests in `tests/services/v1/test_dummy_service.py` (and v2 if applicable) so that responses built via factory contain `uuid` and no `id`.

## Dev Notes

- **Epic context:** Epic 16 introduces a client-facing UUID on the Dummy entity; DTOs expose only `uuid`, never internal `id`. PUT by UUID is Story 16.2.
- **Architecture:** Entities in `models/entities/`; DTOs in `models/dto/v1/` (and v2); factories in `factories/`. Use Pydantic-only mapping. See PROJECT_CONTEXT § Data Persistence and § Adding a New Resource.
- **Current state:** Dummy entity has `id`, `name`, `description` (no uuid). PostDummiesResponse currently exposes `id` — must be removed and replaced with `uuid`.
- **UUID format:** Use standard UUID (e.g. uuid4). Store as string in DB/ORM; validate format in Pydantic if needed.
- **Schema:** Project uses `SQLModel.metadata.create_all(engine)` in lifespan; no Alembic. New column `uuid` on DUMMY table; existing rows need backfill (e.g. generate UUID in lifespan after create_all, or in a seed step).
- **Testing:** Use existing `client` and `session` fixtures; override `get_session` as in conftest. Assert on response JSON keys: `"uuid" in body`, `"id" not in body`.

### Project Structure Notes

- `src/fastapi_archetype/models/entities/dummy.py` — add uuid field.
- `src/fastapi_archetype/models/dto/v1/dummy.py` — add uuid to response DTOs, remove id from PostDummiesResponse.
- `src/fastapi_archetype/factories/dummy.py` — map entity.uuid into response DTOs; do not pass id.
- `tests/api/test_dummy_routes.py`, `tests/api/test_v2_dummy_routes.py`, `tests/services/v1/test_dummy_service.py` — assert uuid present, id absent.

### References

- [Source: .bmad/planning-artifacts/epics/epic-16-entity-uuid-and-put-dummies.md] — Story 16.1 AC and scope.
- [Source: PROJECT_CONTEXT.md] — Data Persistence, DTO naming, Adding a New Resource (uuid on entity, DTOs expose uuid not id).

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Debug Log References

### Completion Notes List

- Added `uuid` to Dummy entity (unique, indexed); backfill in lifespan for existing rows. DTOs expose `uuid` only; removed `id` from PostDummiesResponse. Factory and tests updated.

### File List

- src/fastapi_archetype/models/entities/dummy.py (modified)
- src/fastapi_archetype/models/dto/v1/dummy.py (modified)
- src/fastapi_archetype/factories/dummy.py (modified)
- src/fastapi_archetype/main.py (modified)
- tests/api/test_dummy_routes.py (modified)
- tests/api/test_v2_dummy_routes.py (modified)
- tests/services/v1/test_dummy_service.py (modified)
