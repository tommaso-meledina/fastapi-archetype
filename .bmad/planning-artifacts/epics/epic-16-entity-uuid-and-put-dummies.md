# Epic 16: Entity UUID and PUT Dummies by UUID

## Context

Epic 15 introduced separate entity models and versioned DTOs with a factories layer. Entities have an internal ID (used for persistence); DTOs can have different properties (e.g. computed `nameInitial`). Clients currently do not receive the internal ID in responses, but there is no stable, client-facing identifier for updating a resource. To make the API realistic and secure, we introduce a UUID on the entity, expose only that UUID to clients, and add PUT so clients can update a Dummy by UUID—with the server resolving UUID to entity/ID internally.

## Problem Statement

- **No stable client identifier:** Without a UUID, clients have no durable, opaque identifier to reference a resource (e.g. for updates or links).
- **No update by client identity:** The dummies route has no PUT; we need update semantics keyed by the only identifier clients know—the UUID.
- **Path/body consistency:** When both path and body carry the UUID, they must match; otherwise the request is ambiguous and should be rejected with 400.

## Proposed Epic Goal

1. **Entity has UUID:** The Dummy entity gets a `uuid` property (string/UUID). It is persisted and used for lookups.
2. **DTOs expose UUID only; never ID:** All DTOs returned to clients include `uuid` and never include the internal `id`. This applies to list and single-resource responses.
3. **PUT on dummies:** Implement PUT so clients can update a Dummy’s properties. The handler receives the UUID in both the path and the request body; if they do not match, return **400 Bad Request**. The factory (or service) resolves the Dummy by UUID to obtain the entity/ID, then maps the incoming DTO to the entity and performs the update.

### Behaviour Summary

- **GET responses:** DTOs contain `uuid` (and other allowed fields such as `nameInitial`); they never contain `id`.
- **PUT request:** e.g. `PUT /v1/dummies/{uuid}` with body `{ "uuid": "<same-uuid>", "name": "..." }`. If `body.uuid !== path uuid` → **400 Bad Request**.
- **PUT implementation:** Resolve Dummy by UUID (e.g. in repository/service); if not found → 404; otherwise map body DTO to entity (using resolved entity’s ID), then persist.

## Expected Scope for Implementation

1. **Entity and DTOs:**
   - Add `uuid` (string, UUID format) to the Dummy entity in `models/entities/`.
   - Ensure all Dummy response DTOs include `uuid` and never include `id`. Migrate or seed data so existing rows have UUIDs if applicable.
2. **Dummies route:**
   - Add PUT method (e.g. `PUT /v1/dummies/{uuid}`). Request body includes `uuid` plus updatable fields. Validate path uuid and body uuid match; if not, return 400.
   - Use factory/repository to fetch Dummy by UUID, then map request DTO to entity (with resolved ID) and save.
3. **Factory layer:**
   - DTO → entity for update: accept UUID from request; resolve entity by UUID to get ID; build entity from DTO + resolved ID (and uuid) for update.
4. **Tests and docs:**
   - Tests for: UUID in responses and absence of id; PUT success; PUT with path/body uuid mismatch (400); PUT with unknown uuid (404). Update PROJECT_CONTEXT and “Adding a New Resource” for uuid and PUT-by-UUID pattern.

## Success Criteria

- Dummy entity has a `uuid` field; all Dummy DTOs returned to clients expose `uuid` and never `id`.
- PUT on dummies updates by UUID; path and body both carry UUID; mismatch returns 400; factory/resolution uses UUID to find entity/ID for update.
- PROJECT_CONTEXT (and “Adding a New Resource”) describe the uuid-on-entity and PUT-by-UUID behaviour.

## Stories

### Story 16.1: Add UUID to Entity and DTOs; Never Expose ID to Clients

As a **software engineer**,
I want **the Dummy entity to have a `uuid` (string) and all Dummy DTOs to expose `uuid` and never expose internal `id`**,
so that **clients have a stable, opaque identifier and never see persistence IDs**.

**Acceptance Criteria:**

- **Given** the Dummy entity **When** I inspect it **Then** it has a `uuid` property (string, UUID format) in addition to its existing fields **And** existing rows have UUIDs (migration or seed as needed).
- **Given** any Dummy response DTO (list or single) **When** the API returns data **Then** the response includes `uuid` **And** does not include `id`.
- **Given** the test suite **When** I run it **Then** tests verify that Dummy responses contain `uuid` and do not contain `id` where applicable.

### Story 16.2: Implement PUT on Dummies by UUID with Path/Body Validation

As a **software engineer**,
I want **a PUT method on the dummies route that accepts UUID in path and body, returns 400 if they differ, and updates the Dummy by resolving UUID to entity/ID in the factory**,
so that **clients can update a Dummy using only the UUID**.

**Acceptance Criteria:**

- **Given** `PUT /v1/dummies/{uuid}` with a body that includes `uuid` and updatable fields **When** path `uuid` and body `uuid` match **Then** the corresponding Dummy is updated **And** the response is 200 (or 204) with updated representation (or appropriate success response).
- **Given** the same PUT **When** path `uuid` and body `uuid` do not match **Then** the API returns **400 Bad Request**.
- **Given** PUT with a UUID that does not exist **When** the request is processed **Then** the API returns **404 Not Found**.
- **Given** the factory/repository **When** mapping DTO to entity for this PUT **Then** the implementation fetches the Dummy by UUID to obtain the entity/ID, then builds the entity from the DTO and resolved ID for update (no ID in request body).

### Story 16.3: Update PROJECT_CONTEXT and "Adding a New Resource" for UUID and PUT

As a **developer onboarding to the project**,
I want **PROJECT_CONTEXT and "Adding a New Resource" to describe the entity UUID, DTOs exposing uuid not id, and the PUT-by-UUID pattern with path/body validation**,
so that **new resources can follow the same pattern**.

**Acceptance Criteria:**

- **Given** PROJECT_CONTEXT **When** I read the project structure and conventions **Then** they describe that entities may have a `uuid` for client-facing identity **And** that DTOs expose `uuid` and never internal `id` **And** that PUT can use path + body UUID with 400 when they mismatch.
- **Given** the "Adding a New Resource" instructions **When** they cover update semantics **Then** they include the pattern: UUID on entity, UUID in DTOs, PUT with path and body UUID and validation for match.

## Notes

- Depends on Epic 15 (entities, DTOs, factories in place). Epic 16 is a separate epic.
- URL shape for PUT is assumed to be `PUT /v1/dummies/{uuid}`; confirm with existing versioning and route conventions in the codebase.
- UUID format (e.g. UUIDv4) and storage (e.g. unique index) should be consistent with project standards.
