# Epic 24: Pythonic Redesign — Functions over Classes

Replace the Spring Boot-like provider/contract/facade/factory class hierarchy with idiomatic Python: plain functions, module namespaces, and dict-dispatch (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 27–39).

> **Architectural reversal.** Epic 18 established the ABC contract / default impl / mock impl / factory class hierarchy as a mandatory pattern. That decision prioritized Java/Spring-style explicitness over Python idiom. After peer review, the conclusion is clear: this application must be Pythonic first. The contract/facade/factory class hierarchy adds indirection without commensurate value at this project's scale. This epic deliberately reverts Epic 18's structural choices in favor of plain functions, module namespaces, and dict-dispatch — while preserving the profile-switching capability the pattern was designed to provide.

## Context

The codebase uses a layered class hierarchy in two subsystems:

**Auth subsystem** (6 source files + tests): `AuthProvider` ABC → `NoAuthProvider` / `EntraExternalAuthProvider` classes → `AuthFacade` wrapper → `build_auth_facade` factory → `get_auth_facade` DI shim.

**Service subsystem** (8 source files + tests): `DummyServiceV*Contract` ABCs → `DefaultDummyServiceV*` / `MockDummyServiceV*` classes → `build_dummy_service_v*` factories → `get_dummy_service_v*` DI shims.

Target pattern (auth example):

```python
# auth/none.py
async def authenticate_bearer_token(token: str) -> Principal: ...

# auth/entra.py
def make_entra_auth(settings: AppSettings) -> AuthFunctions:
    jwks_cache: dict[str, Any] = {}
    async def authenticate_bearer_token(token: str) -> Principal: ...
    async def get_client_credentials_token(scope: str) -> str: ...
    return AuthFunctions(authenticate_bearer_token, ...)

# auth/factory.py
def get_auth(settings: AppSettings) -> AuthFunctions:
    return {"none": ..., "entra": ...}[settings.auth_type]
```

## Problem Statement

- **Over-engineering:** ABCs, facades, and class-based factories add layers of indirection for a project that has two auth modes and one service resource.
- **Not Pythonic:** The pattern is modeled on Spring Boot (Java) dependency injection; Python's module system and first-class functions provide equivalent decoupling with less ceremony.
- **Maintenance cost:** Every new service requires an ABC, two class implementations, a factory function, and a DI shim — four files of boilerplate before any logic.

## Proposed Epic Goal

1. **Auth subsystem:** Remove `AuthProvider` and `RoleMappingProvider` ABCs, convert provider classes to plain function modules, remove `AuthFacade`, replace factory with dict-dispatch, rewire DI.
2. **Service subsystem:** Remove service contract ABCs, convert class implementations to plain function modules in a flat directory structure, replace factory with dict-dispatch, rewire routes and DI.
3. **Tests:** Update all affected auth and service tests.
4. **Documentation:** Comprehensive `PROJECT_CONTEXT.md` update per the action 39 checklist.

## Success Criteria

- No ABCs remain in `auth/contracts.py` (error classes are kept).
- `AuthFacade` class and `auth/facade.py` are removed.
- Auth providers are plain function modules (`auth/none.py`, `auth/entra.py`).
- `auth/factory.py` uses dict-dispatch returning configured functions.
- `auth/dependencies.py` wires plain functions directly.
- No service contract ABCs remain in `services/contracts/`.
- Service implementations are plain function modules in flat `services/v*/` directories (no `implementations/` subdirectory).
- `services/factory.py` uses dict-dispatch returning module references or namespaces.
- Route handlers consume plain functions via DI.
- All auth and service tests pass.
- `PROJECT_CONTEXT.md` is updated per the action 39 checklist.
- All quality checks pass.

## Stories

### Story 24.1: Auth Subsystem — Remove ABCs and Facade, Convert to Functions

As a **developer**,
I want **the auth provider ABCs and facade removed and the provider classes converted to plain function modules**,
so that **the auth subsystem uses idiomatic Python without unnecessary class hierarchy**.

**Acceptance Criteria:**

- **Given** `auth/contracts.py` **When** I inspect it **Then** `AuthProvider` and `RoleMappingProvider` ABCs are removed; error classes (`AuthError`, `UnauthorizedError`, etc.) remain.
- **Given** `auth/none.py` (previously `auth/providers/none.py`) **When** I inspect it **Then** it exports plain async functions (e.g. `authenticate_bearer_token`, `get_client_credentials_token`) equivalent to the former `NoAuthProvider` methods.
- **Given** `auth/entra.py` (previously `auth/providers/entra.py`) **When** I inspect it **Then** it uses a closure-based factory (e.g. `make_entra_auth(settings)`) that returns configured async functions, preserving statefulness (JWKS cache, settings) via closure scope.
- **Given** `auth/providers/role_mapping.py` **When** I inspect it **Then** `BasicRoleMappingProvider` is replaced with a plain function (e.g. `def identity_role_mapper(role: str) -> str: return role`).
- **Given** `auth/facade.py` **When** I check **Then** the file is removed; `AuthFacade` no longer exists.
- **Given** the `auth/providers/` directory **When** I check **Then** it is removed or empty; provider modules live directly under `auth/`.

### Story 24.2: Auth Factory and DI Rewire

As a **developer**,
I want **`auth/factory.py` refactored to dict-dispatch and `auth/dependencies.py` rewired to use plain functions**,
so that **auth selection and injection use simple, transparent mechanisms**.

**Acceptance Criteria:**

- **Given** `auth/factory.py` **When** I inspect it **Then** it contains a dict-dispatch function (e.g. `get_auth(settings)`) that returns configured auth functions keyed by `settings.auth_type`.
- **Given** `auth/dependencies.py` **When** I inspect it **Then** `require_auth`, `require_role`, and related dependencies call the auth functions directly (no facade indirection).
- **Given** the application **When** started with `AUTH_TYPE=none` or `AUTH_TYPE=entra` **Then** the correct auth functions are wired and auth behaviour is unchanged.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 24.3: Service Subsystem — Remove Contracts, Flatten to Functions

As a **developer**,
I want **service contract ABCs removed and class implementations converted to plain function modules in a flat directory structure**,
so that **the service layer is simple, flat, and Pythonic**.

**Acceptance Criteria:**

- **Given** `services/contracts/dummy_service.py` **When** I check **Then** `DummyServiceV1Contract` and `DummyServiceV2Contract` ABCs are removed (the file or directory may be removed entirely if empty).
- **Given** `services/v1/` **When** I list files **Then** the `implementations/` subdirectory is gone; service functions live in `services/v1/dummy.py` (default) and `services/v1/mock_dummy.py` (mock).
- **Given** `services/v2/` **When** I list files **Then** the same flat structure applies: `services/v2/dummy.py` and `services/v2/mock_dummy.py`.
- **Given** the service modules **When** I inspect them **Then** they export plain functions (e.g. `get_all_dummies(session)`, `create_dummy(session, dummy)`) not class methods.
- **Given** `services/__init__.py` **When** I inspect it **Then** AOP `apply_logging()` is applied to the new function modules.

### Story 24.4: Service Factory, Routes, and DI Rewire

As a **developer**,
I want **`services/factory.py` refactored to dict-dispatch and route handlers rewired to consume plain functions**,
so that **profile-driven service selection works through simple module dispatch**.

**Acceptance Criteria:**

- **Given** `services/factory.py` **When** I inspect it **Then** it uses dict-dispatch (keyed by `settings.profile`) returning module references or namespaces of functions.
- **Given** `api/v1/dummy_routes.py` and `api/v2/dummy_routes.py` **When** I inspect them **Then** route handlers receive service functions via DI (not class instances) and call them directly.
- **Given** the application **When** started with `PROFILE=default` or `PROFILE=mock` **Then** the correct service functions are wired and behaviour is unchanged.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 24.5: Test Updates and PROJECT_CONTEXT for Pythonic Redesign

As a **developer or agent**,
I want **all affected auth and service tests updated and `PROJECT_CONTEXT.md` rewritten to document the functional patterns**,
so that **tests pass and documentation matches the new architecture**.

**Acceptance Criteria:**

- **Given** `tests/auth/` **When** I run auth tests **Then** all pass against the new function-based auth modules (facade tests are removed or rewritten).
- **Given** `tests/services/` **When** I run service tests **Then** all pass against the new plain-function service modules.
- **Given** `PROJECT_CONTEXT.md` § Authentication and Authorization **When** I read it **Then** it describes the functional pattern (plain functions, closure-based factory for Entra, dict-dispatch).
- **Given** `PROJECT_CONTEXT.md` § Profile and Service Contracts **When** I read it **Then** it describes dict-dispatch and plain functions (no ABCs or class hierarchy).
- **Given** `PROJECT_CONTEXT.md` § Module organization **When** I read it **Then** it reflects the flat `services/v*/` layout with no `contracts/` or `implementations/`.
- **Given** `PROJECT_CONTEXT.md` § Anti-Patterns **When** I read it **Then** "Do not wire routes directly to concrete service classes" is removed **And** new guidance (e.g. "Do not use ABCs or class hierarchies for service contracts") is present.
- **Given** `PROJECT_CONTEXT.md` § Dependency injection **When** I read it **Then** it describes injection of functions (not contract types).
- **Given** `PROJECT_CONTEXT.md` § Adding a New Resource **When** I read steps 5–9 **Then** they describe the functional pattern (plain function modules, dict-dispatch factory, no ABC).
- **Given** `PROJECT_CONTEXT.md` § Project Structure tree **When** I read it **Then** it reflects the new directory layout.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.
