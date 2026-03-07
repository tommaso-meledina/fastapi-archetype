# Story 15.4: Update PROJECT_CONTEXT and "Adding a New Resource"

Status: backlog

## Story

As a **developer onboarding to the project**,
I want **PROJECT_CONTEXT and the "Adding a New Resource" section to describe the entities / dto / factories layout and Pydantic-only mapping**,
so that **new resources follow the same pattern**.

## Acceptance Criteria

1. **Given** PROJECT_CONTEXT **When** I read the project structure and conventions **Then** they describe `models/entities/`, `models/dto/<version>/`, and `factories/` **And** state that entity↔DTO mapping is Pydantic-only.

2. **Given** the "Adding a New Resource" instructions **When** I follow them **Then** they include steps for adding an entity, versioned DTO(s), and factory module **And** no steps reference a single shared model for both ORM and API.

## Tasks / Subtasks

- [ ] Task 1: Update PROJECT_CONTEXT project structure and data persistence (AC: 1)
  - [ ] In "Project Structure": document `models/entities/`, `models/dto/` (with v1, v2 subfolders), `factories/`
  - [ ] In "Data Persistence" (or equivalent): state that ORM uses entity models from `models/entities/`; API uses DTOs from `models/dto/<version>/`; conversion is in `factories/` using Pydantic only
- [ ] Task 2: Update "Adding a New Resource" (AC: 2)
  - [ ] Step 1 (or equivalent): add entity in `models/entities/<resource>.py`
  - [ ] Add step(s): add DTO(s) in `models/dto/v1/<resource>.py` (and v2 when needed)
  - [ ] Add step: add `factories/<resource>.py` with entity_to_dto and dto_to_entity (Pydantic-only)
  - [ ] Remove or replace any instruction that said "one model per file in models/" for both ORM and API
- [ ] Task 3: Update "Module organization" / conventions if present (AC: 1)
  - [ ] Conventions section: one entity per file in `models/entities/`; one DTO file per resource per version in `models/dto/<version>/`; one factory module per entity in `factories/`

## References

- [Source: .bmad/planning-artifacts/epics/epic-separate-entity-dto-and-factories.md#Story 15.4]
