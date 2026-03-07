# Story 15.3: Wire Entities, DTOs, and Factories; Remove Legacy Model

Status: backlog

## Story

As a **software engineer**,
I want **services to use only entities, routes to use only DTOs and factories at the boundary, and the legacy `models/dummy.py` removed**,
so that **the API contract (JSON shape, status codes, paths) is unchanged and all conversion goes through factories**.

## Acceptance Criteria

1. **Given** v1 and v2 dummy routes **When** a request is handled **Then** request bodies are validated as DTOs from `models/dto/v1/` (or v2 when used); responses are built from entities via factory entity→DTO; services accept and return entities only.

2. **Given** the codebase **When** this story is complete **Then** `models/dummy.py` is removed **And** no code imports from it.

3. **Given** the existing test suite **When** I run it **Then** all tests pass **And** client-visible API behaviour (paths, JSON shape, status codes) is unchanged.

## Tasks / Subtasks

- [ ] Task 1: Update services to use entity from `models/entities` (AC: 1)
  - [ ] In `services/v1/dummy_service.py`: import Dummy from `fastapi_archetype.models.entities.dummy`; signatures and logic unchanged (still accept/return entity)
  - [ ] In `services/v2/dummy_service.py`: same change
- [ ] Task 2: Update routes to use DTOs and factories (AC: 1)
  - [ ] In `api/v1/dummy_routes.py`: use DTO from `models/dto/v1/dummy` for `response_model` and request body; after service calls, use factory `entity_to_dto` for response; for POST body use `dto_to_entity` before calling service
  - [ ] In `api/v2/dummy_routes.py`: same pattern
- [ ] Task 3: Remove legacy model and update imports (AC: 2)
  - [ ] Delete `src/fastapi_archetype/models/dummy.py`
  - [ ] Ensure `models/__init__.py` (if it re-exports) no longer exposes old Dummy; remove or update re-exports
  - [ ] Grep for any remaining `models.dummy` or `models/dummy` imports; fix if needed
- [ ] Task 4: Verify tests and API contract (AC: 3)
  - [ ] Run full test suite; all pass
  - [ ] Optionally run existing API tests that assert response JSON shape (camelCase, status codes)

## References

- [Source: .bmad/planning-artifacts/epics/epic-separate-entity-dto-and-factories.md#Story 15.3]
