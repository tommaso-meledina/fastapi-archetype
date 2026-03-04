# Story 11.3: RoleMappingProvider Abstraction

Status: done

## Story

As a **software engineer**,
I want **role checks to resolve internal role labels to external identifiers through a pluggable mapping provider**,
so that **the archetype supports IdP configurations where roles are represented as GUIDs or other non-human-readable identifiers, without coupling the mapping strategy to the auth subsystem**.

## Acceptance Criteria

1. **Given** a `RoleMappingProvider` ABC, **When** I inspect the contract, **Then** it defines a `to_external(role_name: str) -> str` method (string in, string out — no enum coupling).

2. **Given** `BasicRoleMappingProvider`, **When** `to_external("admin")` is called, **Then** it returns `"admin"` (identity mapping).

3. **Given** `require_role` dependency, **When** role enforcement runs, **Then** it calls `role_mapper.to_external(required_role.value)` and checks the result against the principal's roles, **And** the `RoleMappingProvider` is injected via the same settings-driven factory pattern used for `AuthProvider`.

4. **Given** a developer extending the archetype, **When** they implement a custom `RoleMappingProvider` (e.g., env-based or table-based), **Then** they can wire it in by updating the factory without modifying auth dependencies or route handlers.

## Tasks / Subtasks

- [x] Task 1 (AC: 1) Define `RoleMappingProvider` ABC
  - [x] 1.1 Added `RoleMappingProvider` ABC to `contracts.py` with `to_external(role_name: str) -> str`
- [x] Task 2 (AC: 2) Implement `BasicRoleMappingProvider`
  - [x] 2.1 Created `BasicRoleMappingProvider` in `providers/role_mapping.py` with identity mapping
- [x] Task 3 (AC: 3) Wire into factory and facade
  - [x] 3.1 Updated `build_auth_facade` to create and inject `BasicRoleMappingProvider`
  - [x] 3.2 Updated `AuthFacade` to accept `role_mapper` parameter and expose via property
  - [x] 3.3 Updated `require_role` to call `facade.role_mapper.to_external(required_role.value)`
- [x] Task 4 (AC: 1, 2, 3, 4) Tests
  - [x] 4.1 Test: BasicRoleMappingProvider identity mapping for admin, reader, writer
  - [x] 4.2 Test: ABC cannot be instantiated directly
  - [x] 4.3 Test: custom GuidRoleMappingProvider works end-to-end (GUID role grants access, plain string denied)
  - [x] 4.4 Test: facade exposes role_mapper property
  - [x] 4.5 Full regression: 111 tests pass
- [x] Task 5 Full regression and lint check passed

## Dev Notes

### Architecture Compliance

- ABC in `contracts.py` alongside `AuthProvider`
- Implementation in `providers/role_mapping.py`
- Factory creates `BasicRoleMappingProvider` by default
- No new dependencies

### References

- [Source: src/fastapi_archetype/auth/contracts.py]
- [Source: src/fastapi_archetype/auth/providers/role_mapping.py]
- [Source: src/fastapi_archetype/auth/facade.py]
- [Source: src/fastapi_archetype/auth/factory.py]
- [Source: src/fastapi_archetype/auth/dependencies.py]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking

### Debug Log References

### Completion Notes List

- Added `RoleMappingProvider` ABC to `contracts.py` with `to_external(role_name: str) -> str`
- Created `BasicRoleMappingProvider` in `providers/role_mapping.py` (identity mapping)
- Updated `AuthFacade` to accept optional `role_mapper` parameter (defaults to `BasicRoleMappingProvider`)
- Updated `build_auth_facade` to create and inject `BasicRoleMappingProvider`
- Updated `require_role` to use `facade.role_mapper.to_external(required_role.value)` for role comparison
- 11 new tests covering ABC contract, basic provider, facade wiring, and end-to-end GUID mapping
- All 111 tests pass, zero regressions

### File List

- `src/fastapi_archetype/auth/contracts.py` (modified — added RoleMappingProvider ABC)
- `src/fastapi_archetype/auth/providers/role_mapping.py` (new)
- `src/fastapi_archetype/auth/facade.py` (modified — added role_mapper parameter and property)
- `src/fastapi_archetype/auth/factory.py` (modified — creates and injects BasicRoleMappingProvider)
- `src/fastapi_archetype/auth/dependencies.py` (modified — uses facade.role_mapper.to_external)
- `tests/auth/test_role_mapping.py` (new)
