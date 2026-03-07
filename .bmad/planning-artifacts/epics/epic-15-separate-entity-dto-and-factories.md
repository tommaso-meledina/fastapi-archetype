# Epic 15: Separate Entity Models, Versioned DTOs, and Factories

## Context

The application currently defines a single model per resource (e.g. `Dummy` in `models/dummy.py`) using SQLModel with `table=True`. That class is used both as the ORM entity (database and services) and as the web contract (request/response bodies in API routes). This dual use is documented in PROJECT_CONTEXT and works for the trivial demo, but it couples API shape to persistence and prevents independent evolution of API versions and database schema.

## Problem Statement

- **Tight coupling:** The same class drives DB writes and HTTP JSON; changing one implies changing the other.
- **No API versioning of contracts:** In real services, request/response shapes often differ by API version; the current layout has no place for version-specific DTOs.
- **No clear mapping layer:** There is no explicit boundary between “domain/persistence” and “web”; mapping logic would be scattered if we added versioned or divergent shapes.

## Proposed Epic Goal

Evolve the codebase so that:

1. **Entity models** live in a dedicated submodule and are used only for persistence.
2. **Web DTOs** live in a versioned submodule and are used only for API request/response.
3. **A factories module** provides the mapping between entities and DTOs in one place per entity.
4. **Mapping is Pydantic-only** (no extra mapping library): use `model_validate()`, `model_dump()`, and explicit field handling where needed.

### Target Structure

- **`models/entities/`** — One file per entity (e.g. `dummy.py`). SQLModel classes with `table=True`; ORM only.
- **`models/dto/`** — Versioned by API version. Subfolders `v1/`, `v2/`, … each with one file per resource (e.g. `models/dto/v1/dummy.py`, `models/dto/v2/dummy.py`). Plain Pydantic models (no `table=True`), with existing API conventions (e.g. camelCase aliases). **DTO naming is mandatory:** `<Method><Resource><Request|Response>` (e.g. `PostDummiesRequest`, `GetDummiesResponse`, `PostDummiesResponse`). Resource name is plural (PascalCase); do not name after the entity (e.g. avoid `DummyCreate`, `DummyResponse`).
- **`factories/`** — New top-level package (same level as `models/`). One file per entity (e.g. `factories/dummy.py`) with:
  - **Entity → DTO:** e.g. `entity_to_dto(entity, dto_cls)` or version-specific helpers.
  - **DTO → Entity:** e.g. `dto_to_entity(dto)` for create/update (e.g. omitting `id` when creating).

Directory name for DTOs is **`models/dto`** (singular), not `models/dtos`.

### Mapping Approach

- Use Pydantic’s built-in conversion: `DTO.model_validate(entity)` and `Entity(**dto.model_dump(...))` with `exclude_unset` / `exclude` as needed.
- No new dependencies; no Adaptix or other mapping library. If conversion complexity grows later, the epic can be revisited to consider a dedicated mapper (with tech-stack approval).

## Expected Scope for Implementation

1. **Refactor `models/`:**
   - Add `models/entities/` and move (or introduce) entity classes there (e.g. `Dummy` with `table=True`).
   - Add `models/dto/v1/` (and later `v2/` when needed); add DTO classes for the dummy resource under `v1` with same camelCase behaviour as today.
2. **Add `factories/`:**
   - One module per entity with functions: entity → DTO, DTO → entity (Pydantic-only implementation).
3. **Wire usage:**
   - Services and routes use entities for DB work and DTOs for request/response; routes call factory functions to convert at the boundary.
4. **Tests and docs:**
   - Update tests and PROJECT_CONTEXT (and “Adding a New Resource”) to describe the entities / dto / factories layout and Pydantic-only mapping.
5. **Backward compatibility:** API contract (JSON shape, status codes, paths) remains unchanged; only internal structure and module layout change.

## Success Criteria

- Entities exist only under `models/entities/` and are not used as FastAPI request/response models.
- DTOs exist only under `models/dto/<version>/` and are used for API input/output only.
- All entity ↔ DTO conversion goes through `factories/` using Pydantic-only code.
- Existing dummy endpoints behave the same from the client’s perspective; tests pass.

## Stories

### Story 15.1: Add Entity and Versioned DTO Structure

As a **software engineer**,
I want **entity models under `models/entities/` and web DTOs under `models/dto/v1/` (and later `v2/`)**,
so that **persistence and API contracts can evolve independently and version-specific shapes have a clear place**.

**Acceptance Criteria:**

- **Given** the codebase **When** this story is complete **Then** `models/entities/dummy.py` exists with the Dummy SQLModel (table=True, same schema as today) **And** `models/dto/v1/dummy.py` exists with DTO class(es) for request/response with the same camelCase behaviour as the current API.
- **Given** the new layout **When** I inspect the project **Then** the existing `models/dummy.py` is unchanged and still used by services and routes (no behavioural change yet).
- **Given** the test suite **When** I run it **Then** all tests still pass.

### Story 15.2: Add Factories Module

As a **software engineer**,
I want **a `factories/` package with one module per entity providing entity ↔ DTO mapping (Pydantic-only)**,
so that **conversion between persistence and web layers is explicit and centralized**.

**Acceptance Criteria:**

- **Given** the `factories/` package **When** I inspect it **Then** `factories/dummy.py` exists with at least: a function to map entity → DTO and a function to map DTO → entity (e.g. for create, omitting `id` when appropriate).
- **Given** the mapping implementation **When** I review it **Then** it uses only Pydantic (`model_validate`, `model_dump`) with no additional mapping library.
- **Given** the new module **When** the application is imported **Then** no existing behaviour changes; routes and services still use the current model (factories are not yet wired).

### Story 15.3: Wire Entities, DTOs, and Factories; Remove Legacy Model

As a **software engineer**,
I want **services to use only entities, routes to use only DTOs and factories at the boundary, and the legacy `models/dummy.py` removed**,
so that **the API contract (JSON shape, status codes, paths) is unchanged and all conversion goes through factories**.

**Acceptance Criteria:**

- **Given** v1 and v2 dummy routes **When** a request is handled **Then** request bodies are validated as DTOs from `models/dto/v1/` (or v2 when used); responses are built from entities via factory entity→DTO; services accept and return entities only.
- **Given** the codebase **When** this story is complete **Then** `models/dummy.py` is removed **And** no code imports from it.
- **Given** the existing test suite **When** I run it **Then** all tests pass **And** client-visible API behaviour (paths, JSON shape, status codes) is unchanged.

### Story 15.4: Update PROJECT_CONTEXT and "Adding a New Resource"

As a **developer onboarding to the project**,
I want **PROJECT_CONTEXT and the "Adding a New Resource" section to describe the entities / dto / factories layout and Pydantic-only mapping**,
so that **new resources follow the same pattern**.

**Acceptance Criteria:**

- **Given** PROJECT_CONTEXT **When** I read the project structure and conventions **Then** they describe `models/entities/`, `models/dto/<version>/`, and `factories/` **And** state that entity↔DTO mapping is Pydantic-only.
- **Given** the "Adding a New Resource" instructions **When** I follow them **Then** they include steps for adding an entity, versioned DTO(s), and factory module **And** no steps reference a single shared model for both ORM and API.

## Notes

- Current dummy implementation can ship with DTOs only under `models/dto/v1/`; v2 structure is in place for when version-specific DTOs are added.
- PROJECT_CONTEXT and dependency list remain unchanged (no new libraries).

## DTO naming convention (mandatory)

Web DTO class names **must** follow: **`<Method><Resource><Request|Response>`**

- **Method:** HTTP method in PascalCase (`Get`, `Post`, `Put`, `Patch`, `Delete`).
- **Resource:** Plural resource name in PascalCase, matching the path (e.g. `Dummies` for `/dummies`).
- **Suffix:** `Request` for request bodies, `Response` for response bodies.

This is documented as a mandatory convention in PROJECT_CONTEXT (Conventions and Patterns → DTO naming, and Anti-Patterns).
