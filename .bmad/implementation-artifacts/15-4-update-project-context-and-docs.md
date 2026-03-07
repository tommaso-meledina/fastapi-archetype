# Story 15.4: Update PROJECT_CONTEXT and "Adding a New Resource"

Status: done

## Story

As a **developer onboarding to the project**,
I want **PROJECT_CONTEXT and the "Adding a New Resource" section to describe the entities / dto / factories layout and Pydantic-only mapping**,
so that **new resources follow the same pattern**.

## Acceptance Criteria

1. **Given** PROJECT_CONTEXT **When** I read the project structure and conventions **Then** they describe `models/entities/`, `models/dto/<version>/`, and `factories/` **And** state that entity↔DTO mapping is Pydantic-only.
2. **Given** the "Adding a New Resource" instructions **When** I follow them **Then** they include steps for adding an entity, versioned DTO(s), and factory module **And** no steps reference a single shared model for both ORM and API.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Update PROJECT_CONTEXT structure and Data Persistence
  - [x] Update Project Structure diagram: replace single `models/dummy.py` with `models/entities/`, `models/dto/v1/`, and `factories/`.
  - [x] Update Data Persistence section: describe entities (ORM only in `models/entities/`), DTOs (API only in `models/dto/<version>/`), and factories (entity↔DTO mapping using only Pydantic `model_validate`/`model_dump`).
  - [x] Update Module organization: one entity per file in `models/entities/`, DTOs in `models/dto/<version>/`, one factory module per entity in `factories/`.
- [x] Task 2 (AC: #2) — Update "Adding a New Resource"
  - [x] Replace single-model steps with: add entity in `models/entities/`, add DTO(s) in `models/dto/v1/`, add factory in `factories/`; routes use DTOs and factories at boundary; services use entities only.

## Dev Agent Record

### Completion Notes List

- Updated PROJECT_CONTEXT: project structure, Data Persistence (entities/DTOs/factories, Pydantic-only mapping), module organization, and "Adding a New Resource" with entity, DTO(s), and factory steps.

### File List

- PROJECT_CONTEXT.md (modified)
