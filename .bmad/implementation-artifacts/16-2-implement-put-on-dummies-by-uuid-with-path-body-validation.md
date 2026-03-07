# Story 16.2: Implement PUT on Dummies by UUID with Path/Body Validation

Status: done

## Story

As a **software engineer**,
I want **a PUT method on the dummies route that accepts UUID in path and body, returns 400 if they differ, and updates the Dummy by resolving UUID to entity/ID in the factory**,
so that **clients can update a Dummy using only the UUID**.

## Acceptance Criteria

1. **Given** `PUT /v1/dummies/{uuid}` with a body that includes `uuid` and updatable fields **When** path `uuid` and body `uuid` match **Then** the corresponding Dummy is updated **And** the response is 200 (or 204) with updated representation (or appropriate success response).
2. **Given** the same PUT **When** path `uuid` and body `uuid` do not match **Then** the API returns **400 Bad Request**.
3. **Given** PUT with a UUID that does not exist **When** the request is processed **Then** the API returns **404 Not Found**.
4. **Given** the factory/repository **When** mapping DTO to entity for this PUT **Then** the implementation fetches the Dummy by UUID to obtain the entity/ID, then builds the entity from the DTO and resolved ID for update (no ID in request body).

## Tasks / Subtasks

- [x] Task 1 (AC: #1,#4) — Service and factory for update by UUID
  - [x] Add `get_dummy_by_uuid(session, uuid) -> Dummy | None` in dummy_service (v1).
  - [x] Add `update_dummy(session, entity: Dummy) -> Dummy` in dummy_service (v1).
  - [x] Add `PutDummiesRequest` DTO (uuid + updatable fields e.g. name, description) and `put_dto_to_entity(existing, dto)` in factory that builds entity from DTO and resolved entity for update.
- [x] Task 2 (AC: #1,#2,#3) — PUT route and validation
  - [x] Add `PUT /v1/dummies/{uuid}` route; body: PutDummiesRequest. If path uuid != body uuid → 400; if not found by uuid → 404; else update and return 200 with updated representation.
  - [x] Add ErrorCode BAD_REQUEST for 400.
- [x] Task 3 (AC: #1–#4) — Tests
  - [x] Test PUT success: update and 200 with updated body (uuid, name, description).
  - [x] Test PUT path/body uuid mismatch → 400.
  - [x] Test PUT unknown uuid → 404.
  - [x] Factory builds entity from DTO and resolved ID; no ID in request body.

## Dev Notes

- Epic 16.1 added uuid to entity and DTOs; this story adds PUT by UUID. URL: `PUT /v1/dummies/{uuid}`. Request body must include `uuid` and updatable fields; path and body uuid must match.
- Use DUMMY_NOT_FOUND for 404. Add BAD_REQUEST or UUID_MISMATCH for 400 when path and body uuid differ.
- Factory: accept session + uuid + PutDummiesRequest; get entity by uuid; if None raise/return 404 at route level; build entity from dto with resolved id and uuid for update.

### References

- [Source: .bmad/planning-artifacts/epics/epic-16-entity-uuid-and-put-dummies.md]
- [Source: PROJECT_CONTEXT.md] — Data Persistence, Adding a New Resource (PUT with path+body UUID).

## Dev Agent Record

### Completion Notes List

- Added PutDummiesRequest, get_dummy_by_uuid, update_dummy (merge), put_dto_to_entity; PUT /v1/dummies/{uuid} with path/body validation (400), 404, 200 with GetDummiesResponse. Tests for success, 400, 404.

### File List

- src/fastapi_archetype/core/errors.py (modified)
- src/fastapi_archetype/models/dto/v1/dummy.py (modified)
- src/fastapi_archetype/factories/dummy.py (modified)
- src/fastapi_archetype/services/v1/dummy_service.py (modified)
- src/fastapi_archetype/api/v1/dummy_routes.py (modified)
- tests/api/test_dummy_routes.py (modified)
