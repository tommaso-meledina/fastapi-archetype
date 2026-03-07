# Story 15.2: Add Factories Module

Status: backlog

## Story

As a **software engineer**,
I want **a `factories/` package with one module per entity providing entity ↔ DTO mapping (Pydantic-only)**,
so that **conversion between persistence and web layers is explicit and centralized**.

## Acceptance Criteria

1. **Given** the `factories/` package **When** I inspect it **Then** `factories/dummy.py` exists with at least: a function to map entity → DTO and a function to map DTO → entity (e.g. for create, omitting `id` when appropriate).

2. **Given** the mapping implementation **When** I review it **Then** it uses only Pydantic (`model_validate`, `model_dump`) with no additional mapping library.

3. **Given** the new module **When** the application is imported **Then** no existing behaviour changes; routes and services still use the current model (factories are not yet wired).

## Tasks / Subtasks

- [ ] Task 1: Create `factories/` package and dummy factory (AC: 1, 2)
  - [ ] Add `src/fastapi_archetype/factories/__init__.py`
  - [ ] Add `src/fastapi_archetype/factories/dummy.py` with:
    - [ ] `entity_to_dto(entity)` → DTO (using DTO from `models/dto/v1/dummy.py` and `model_validate` or equivalent)
    - [ ] `dto_to_entity(dto)` → entity for create (e.g. exclude `id` via `model_dump(exclude_unset=True)` or explicit field copy)
  - [ ] Use only Pydantic/SQLModel built-ins; no Adaptix or other mapper
- [ ] Task 2: Verify no wiring yet (AC: 3)
  - [ ] Confirm routes and services still import from `models.dummy`; no route or service imports from `factories`
  - [ ] Run full test suite; all pass

## References

- [Source: .bmad/planning-artifacts/epics/epic-separate-entity-dto-and-factories.md#Story 15.2]
