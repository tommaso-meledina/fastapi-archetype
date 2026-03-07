# Story 15.3: Wire Entities, DTOs, and Factories; Remove Legacy Model

Status: done

## Story

As a **software engineer**,
I want **services to use only entities, routes to use only DTOs and factories at the boundary, and the legacy `models/dummy.py` removed**,
so that **the API contract (JSON shape, status codes, paths) is unchanged and all conversion goes through factories**.

## Acceptance Criteria

1. **Given** v1 and v2 dummy routes **When** a request is handled **Then** request bodies are validated as DTOs from `models/dto/v1/` (or v2 when used); responses are built from entities via factory entity→DTO; services accept and return entities only.
2. **Given** the codebase **When** this story is complete **Then** `models/dummy.py` is removed **And** no code imports from it.
3. **Given** the existing test suite **When** I run it **Then** all tests pass **And** client-visible API behaviour (paths, JSON shape, status codes) is unchanged.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Wire v1 routes and service to entities/DTOs/factories
  - [x] Update `api/v1/dummy_routes.py`: use `DummyCreate` for POST body, `DummyResponse` for GET/POST response; use factory `dto_to_entity` for request, `entity_to_dto` for responses; keep session and auth unchanged.
  - [x] Update `services/v1/dummy_service.py`: use entity `Dummy` from `models.entities.dummy`; accept and return entities only.
- [x] Task 2 (AC: #1) — Wire v2 routes and service to entities/DTOs/factories
  - [x] Same as Task 1 for `api/v2/dummy_routes.py` and `services/v2/dummy_service.py`.
- [x] Task 3 (AC: #2, #3) — Remove legacy model
  - [x] Delete `models/dummy.py`. Ensure no imports from `fastapi_archetype.models.dummy` remain. Run full test suite; confirm API behaviour unchanged.

## Dev Notes

- Routes: request body → DTO (DummyCreate); response → DTO (DummyResponse) built via entity_to_dto(entity). Services: receive/return entity only.
- **Source:** [Epic 15](.bmad/planning-artifacts/epics/epic-15-separate-entity-dto-and-factories.md), [factories/dummy.py](src/fastapi_archetype/factories/dummy.py).

## Dev Agent Record

### Agent Model Used

-

### Completion Notes List

- Wired v1 and v2 dummy routes to use DummyCreate/DummyResponse and factories; services use entity Dummy from models.entities.dummy. Removed models/dummy.py; updated service tests to import entity. All 168 tests pass; API behaviour unchanged.

### File List

- src/fastapi_archetype/api/v1/dummy_routes.py (modified)
- src/fastapi_archetype/api/v2/dummy_routes.py (modified)
- src/fastapi_archetype/services/v1/dummy_service.py (modified)
- src/fastapi_archetype/services/v2/dummy_service.py (modified)
- tests/services/v1/test_dummy_service.py (modified)
- tests/services/v2/test_dummy_service.py (modified)
- src/fastapi_archetype/models/dummy.py (deleted)
