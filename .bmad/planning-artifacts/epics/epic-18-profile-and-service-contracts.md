# Epic 18: Profile and Service Contracts (PoC via Dummies)

A developer can run the application with an optional `PROFILE` environment variable (`"default"` or `"mock"`). When `profile` is `"default"`, the real (database-backed) dummy service implementations are wired; when `profile` is `"mock"`, mock implementations that return data without connecting to the database are wired. The dummies feature is refactored so that every consumer depends on a **service contract** (interface), with a default and a mock implementation selected by the factory based on `profile`. This epic implements the proof-of-concept of the pattern documented in PROJECT_CONTEXT §11 (Profile and Service Contracts) and in the architecture docs (core-architectural-decisions.md, implementation-patterns-consistency-rules.md).

## Context

The application currently wires routes directly to concrete service modules (e.g. `services.v1.dummy_service`). There is no abstraction (contract) for the dummy service, and no way to run with a mock implementation without changing code or overriding dependencies in tests. The tech design has been updated to establish the profile and service-contract pattern for all services; this epic implements that pattern for the dummies resource (v1 and v2) as the reference implementation.

## Problem Statement

- **Tight coupling:** Routes import and call concrete service modules; swapping implementations (e.g. for local dev without a database) requires code or test overrides.
- **No profile concept:** There is no single switch to choose “real” vs “mock” behaviour across services.
- **No contract:** New services are added as concrete modules only; there is no enforced interface or mock implementation.

## Proposed Epic Goal

1. **Introduce optional `PROFILE`** on `AppSettings`: values `"default"` | `"mock"`, default `"default"`. Document in `.env.example`.
2. **Define a service contract for dummies (v1):** An ABC (or Protocol) declaring `get_all_dummies(session)`, `get_dummy_by_uuid(session, uuid)`, `create_dummy(session, dummy)`, `update_dummy(session, entity)` with the existing entity/session types.
3. **Default implementation (v1):** Move current `services/v1/dummy_service.py` logic into a class (or module) that implements the contract and uses the database (current behaviour). Keep metrics and error handling.
4. **Mock implementation (v1):** New implementation that satisfies the same contract but uses in-memory storage (or hard-coded data); no database or external calls.
5. **Factory and DI (v1):** Add `build_dummy_service(settings)` that returns the default or mock implementation based on `settings.profile`. Expose a FastAPI dependency (e.g. `get_dummy_service`) used by v1 routes. Wire v1 dummy routes to depend on this dependency instead of importing the concrete module.
6. **Apply the same pattern to v2 dummies:** Contract for v2 (e.g. `get_all_dummies`, `create_dummy` only), default impl (current v2 logic), mock impl, factory/dependency, wire v2 routes.
7. **Tests:** Verify that with `PROFILE=default` the app uses the database-backed implementation and with `PROFILE=mock` the app uses the mock; add/update unit tests for default and mock implementations; ensure existing route tests still pass (with dependency override or profile as needed).

## Success Criteria

- `AppSettings` has a `profile` field (`Literal["default", "mock"]`, default `"default"`). `.env.example` documents `PROFILE`.
- A single contract exists for the v1 dummies service and is implemented by a default (database) and a mock (in-memory) implementation. v2 has a contract and default/mock implementations consistent with v2’s current API (get_all, create).
- A factory function selects the implementation based on `settings.profile`; a FastAPI dependency provides the chosen instance to routes.
- v1 and v2 dummy routes depend on the service via the dependency (contract type), not via direct import of a concrete module.
- With `PROFILE=mock`, GET/POST (and PUT for v1) on dummies return data without requiring a database. With `PROFILE=default`, behaviour is unchanged from current (database-backed).
- All existing tests pass; new or updated tests cover profile-driven selection and mock/default implementations.
- PROJECT_CONTEXT and architecture docs already describe the pattern; this epic does not duplicate them but implements the PoC as specified there.

## Stories

### Story 18.1: Add Profile to Configuration

As a **developer or operator**,
I want **an optional `PROFILE` environment variable (`"default"` or `"mock"`) with default `"default"`**,
so that **the application can later wire service implementations based on profile**.

**Acceptance Criteria:**

- **Given** `core/config.py` **When** this story is complete **Then** `AppSettings` has a field `profile` with type `Literal["default", "mock"]` and default `"default"` **And** the field is validated so that only these two values are accepted (fail fast at startup if invalid).
- **Given** `.env.example` **When** I read it **Then** it documents optional `PROFILE` with allowed values and default behaviour.
- **Given** the test suite **When** I run tests that load config **Then** they are updated if they previously assumed no `profile` field (e.g. assert default or explicit profile).

### Story 18.2: Dummy Service Contract, Default and Mock Implementations, and Wiring (v1)

As a **developer**,
I want **the v1 dummies feature to use a service contract with a default (database) and a mock (in-memory) implementation, selected by `profile` via a factory and injected into routes**,
so that **I can run with `PROFILE=mock` and get dummies without a database, and the pattern is established for v1**.

**Acceptance Criteria:**

- **Given** `services/contracts/dummy_service.py` (or equivalent) **When** I inspect it **Then** it defines an ABC (or Protocol) for the v1 dummy service with methods: `get_all_dummies(session) -> list[Dummy]`, `get_dummy_by_uuid(session, uuid) -> Dummy | None`, `create_dummy(session, dummy) -> Dummy`, `update_dummy(session, entity) -> Dummy`. Signatures use the existing entity and `Session` types.
- **Given** the current v1 dummy service logic **When** this story is complete **Then** it lives in a default implementation (e.g. `services/v1/implementations/default_dummy_service.py`) that implements the contract and uses the database; metrics and `AppException(ErrorCode.DUMMY_NOT_FOUND)` behaviour are preserved.
- **Given** a new mock implementation (e.g. `services/v1/implementations/mock_dummy_service.py`) **When** I inspect it **Then** it implements the same contract **And** returns data from in-memory storage (or hard-coded data) without using the database **And** supports list, get by UUID, create, and update in a way that is consistent enough for route-level tests (e.g. in-memory list keyed by UUID).
- **Given** a factory function (e.g. in `services/factory.py`) **When** `settings.profile == "default"` **Then** it returns the default implementation **When** `settings.profile == "mock"` **Then** it returns the mock implementation.
- **Given** a FastAPI dependency (e.g. `get_dummy_service`) **When** used in v1 routes **Then** it provides the implementation returned by the factory (e.g. by reading settings and calling the factory).
- **Given** v1 dummy routes **When** this story is complete **Then** they depend on the service via `Depends(get_dummy_service)` (or equivalent) and call methods on the injected contract **And** they do not import the concrete default or mock module.
- **Given** `services/__init__.py` **When** I inspect it **Then** AOP logging is applied to the implementation modules as appropriate.
- **Given** the full test suite **When** I run it **Then** existing v1 dummy route and service tests pass (adjustments may include overriding the service dependency with the default impl and a session, or setting `PROFILE=default` and using the real implementation).

### Story 18.3: Apply Profile and Service Contract Pattern to v2 Dummies

As a **developer**,
I want **the v2 dummies feature to use the same profile-driven contract pattern (contract, default impl, mock impl, factory, DI)**,
so that **v2 dummies also switch by `PROFILE` and the pattern is consistent across versions**.

**Acceptance Criteria:**

- **Given** v2 dummies **When** this story is complete **Then** a v2 dummy service contract exists (methods: at least `get_all_dummies(session)`, `create_dummy(session, dummy)` to match current v2 API) **And** a default implementation (current v2 logic, with metrics and logging) and a mock implementation exist **And** a factory (or extended factory) returns the v2 implementation based on `settings.profile` **And** v2 routes depend on the service via a dependency (e.g. `Depends(get_dummy_service_v2)`) and do not import the concrete module.
- **Given** `PROFILE=mock` **When** I call GET or POST on `/v2/dummies` **Then** the mock implementation is used and no database is required.
- **Given** the full test suite **When** I run it **Then** all v2 dummy tests pass.

### Story 18.4: Tests for Profile-Driven Service Selection and Implementations

As a **software engineer**,
I want **tests that verify profile-driven selection and the behaviour of default and mock dummy implementations**,
so that **regressions are caught and the PoC is validated**.

**Acceptance Criteria:**

- **Given** the application started with `PROFILE=default` **When** I call GET/POST (and PUT for v1) on dummies **Then** a test asserts that the database-backed implementation is used (e.g. data persists across requests, or a test uses a real session and default impl). Existing endpoint tests that use the database remain valid.
- **Given** the application started with `PROFILE=mock` **When** I call GET/POST (and PUT for v1) on dummies **Then** a test asserts that the mock implementation is used (e.g. no database required, or mock-specific behaviour). At least one test per version (v1, v2) that runs with `PROFILE=mock` and verifies list and create (and update for v1) without a real DB.
- **Given** unit tests for the default and mock implementations **When** I run them **Then** they test the contract methods in isolation (default impl with a real or test session; mock impl with in-memory state).
- **Given** the full test suite **When** I run it **Then** all tests pass **And** coverage remains at or above the project target (>90% where applicable).
- **Given** test configuration **When** tests need a specific profile or service override **Then** they use `app.dependency_overrides` or set `PROFILE` in the environment as appropriate; no test assumes a single global profile without intent.

## Notes

- **Contract location:** The pattern in PROJECT_CONTEXT places contracts in `services/contracts/`. One contract per logical service; v1 and v2 may share one contract (with v2 impl implementing a subset or raising for unsupported methods) or use two contracts—implementation choice should match the documented structure.
- **Session in mock:** The mock implementation may accept a `Session` parameter for signature compatibility but ignore it; callers (routes) still pass the session from `Depends(get_session)` so that the same route code works for both implementations.
- **Metrics in mock:** The mock implementation may or may not increment the same Prometheus counters; product decision (e.g. skip in mock to avoid inflating metrics, or increment for consistency). Document in implementation.
- **v2 contract scope:** v2 currently has no PUT or get-by-UUID; the v2 contract need only include the methods v2 routes use. The v2 default and mock implementations implement only those methods.
