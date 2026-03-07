# Story 15.2: Add Factories Module

Status: done

## Story

As a **software engineer**,
I want **a `factories/` package with one module per entity providing entity ↔ DTO mapping (Pydantic-only)**,
so that **conversion between persistence and web layers is explicit and centralized**.

## Acceptance Criteria

1. **Given** the `factories/` package **When** I inspect it **Then** `factories/dummy.py` exists with at least: a function to map entity → DTO and a function to map DTO → entity (e.g. for create, omitting `id` when appropriate).
2. **Given** the mapping implementation **When** I review it **Then** it uses only Pydantic (`model_validate`, `model_dump`) with no additional mapping library.
3. **Given** the new module **When** the application is imported **Then** no existing behaviour changes; routes and services still use the current model (factories are not yet wired).

## Tasks / Subtasks

- [x] Task 1 (AC: #1, #2) — Add factories package and dummy factory
  - [x] Create `src/fastapi_archetype/factories/` package.
  - [x] Create `factories/dummy.py` with: entity → DTO (e.g. entity to DummyResponse) and DTO → entity (e.g. DummyCreate to entity for create, omitting `id`). Use only Pydantic: `model_validate()`, `model_dump()`, `exclude_unset`/`exclude` as needed.
- [x] Task 2 (AC: #3) — Do not wire factories yet
  - [x] Do not change routes, services, or any imports from `models.dummy`. Ensure app still runs and all tests pass.

## Dev Notes

- Epic 15: factories provide the mapping layer; this story adds the module only; story 15.3 will wire routes/services and remove legacy model.
- **Entity → DTO:** e.g. `entity_to_dto(entity, dto_cls)` or version-specific helper; use `dto_cls.model_validate(entity)` or equivalent Pydantic conversion.
- **DTO → Entity:** e.g. `dto_to_entity(dto)` for create; build entity from dto `model_dump(exclude_unset=True)` or `exclude={'id'}` so `id` is not set on create.
- **No new dependencies:** Pydantic-only; no Adaptix or other mapping library.
- **Source:** [Epic 15](.bmad/planning-artifacts/epics/epic-15-separate-entity-dto-and-factories.md), [PROJECT_CONTEXT](PROJECT_CONTEXT.md).

### References

- [Source: epic-15-separate-entity-dto-and-factories.md] — Factories module, Pydantic-only mapping.
- [Source: models/entities/dummy.py, models/dto/v1/dummy.py] — Entity and DTO classes to map.

## Dev Agent Record

### Agent Model Used

-

### Debug Log References

### Completion Notes List

- Added `factories/` package with `dummy.py` providing `entity_to_dto` (entity → DummyResponse) and `dto_to_entity` (DummyCreate → entity) using only `model_dump()` and `model_validate()`. No routes/services changed; all 168 tests pass.

### File List

- src/fastapi_archetype/factories/__init__.py (new)
- src/fastapi_archetype/factories/dummy.py (new)
