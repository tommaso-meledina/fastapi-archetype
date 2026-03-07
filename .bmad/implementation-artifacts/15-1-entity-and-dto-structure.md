# Story 15.1: Add Entity and Versioned DTO Structure

Status: backlog

## Story

As a **software engineer**,
I want **entity models under `models/entities/` and web DTOs under `models/dto/v1/` (and later `v2/`)**,
so that **persistence and API contracts can evolve independently and version-specific shapes have a clear place**.

## Acceptance Criteria

1. **Given** the codebase **When** this story is complete **Then** `models/entities/dummy.py` exists with the Dummy SQLModel (table=True, same schema as today) **And** `models/dto/v1/dummy.py` exists with DTO class(es) for request/response with the same camelCase behaviour as the current API.

2. **Given** the new layout **When** I inspect the project **Then** the existing `models/dummy.py` is unchanged and still used by services and routes (no behavioural change yet).

3. **Given** the test suite **When** I run it **Then** all tests still pass.

## Tasks / Subtasks

- [ ] Task 1: Create `models/entities/` package and move Dummy entity (AC: 1)
  - [ ] Add `src/fastapi_archetype/models/entities/__init__.py`
  - [ ] Add `src/fastapi_archetype/models/entities/dummy.py` with Dummy(SQLModel, table=True), same fields and `__tablename__` as current `models/dummy.py`
  - [ ] Keep `models/dummy.py` unchanged (still the single source used by callers)
- [ ] Task 2: Create `models/dto/v1/` and Dummy DTO(s) (AC: 1)
  - [ ] Add `src/fastapi_archetype/models/dto/__init__.py` and `models/dto/v1/__init__.py`
  - [ ] Add `src/fastapi_archetype/models/dto/v1/dummy.py` with Pydantic model(s) for request/response (camelCase alias_generator, same shape as current API)
- [ ] Task 3: Verify tests and behaviour unchanged (AC: 2, 3)
  - [ ] Run full test suite; all pass
  - [ ] Confirm no imports yet reference `models/entities` or `models/dto` (optional sanity check)

## References

- [Source: .bmad/planning-artifacts/epics/epic-separate-entity-dto-and-factories.md#Story 15.1]
