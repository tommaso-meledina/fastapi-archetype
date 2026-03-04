# Epic 10: External IdP Authentication and Role-Based Access Control

A developer can see external IdP-based bearer-token authentication and RBAC integrated into the application, with explicit per-route protection via FastAPI dependencies and a clear extension point for additional providers.

**New libraries required:**
- `python-jose[cryptography]` — JWT parsing/signature verification
- `httpx` — async outbound calls to discovery/JWKS/token/Graph endpoints

## Story 10.1: External IdP Authentication Infrastructure

As a **software engineer**,
I want **authentication to rely on externally issued bearer tokens (remote IdP) rather than local credential validation**,
So that **services based on this archetype can integrate with enterprise identity platforms without implementing local username/password auth flows**.

**Acceptance Criteria:**

**Given** `AppSettings` defines authentication mode and provider settings
**When** I inspect configuration behavior
**Then** `AUTH_TYPE` supports `none` and `entra`
**And** `AUTH_TYPE=entra` requires issuer, discovery/JWKS, token endpoint, client id, and client secret settings

**Given** the application runs with `AUTH_TYPE=entra`
**When** a protected endpoint receives a bearer token
**Then** the token is validated against remote JWKS keys
**And** issuer validation is enforced
**And** audience validation is enforced only when `AUTH_EXTERNAL_AUDIENCE` is configured
**And** token claims are mapped into a typed principal model

**Given** token validation fails (missing, malformed, invalid signature, expired, bad issuer/audience)
**When** I call a protected endpoint
**Then** the response is a 401 with the application's structured error format

**Given** the authentication implementation
**When** I inspect the code
**Then** it uses `fastapi.security.HTTPBearer` to extract bearer tokens
**And** it performs async outbound OAuth/IdP calls via provider-specific implementations behind an auth facade
**And** it does not expose a local token-issuance endpoint

**Given** the application runs with `AUTH_TYPE=none`
**When** protected endpoints are called without a token
**Then** requests are treated as authenticated for local development via a deterministic stub principal

## Story 10.2: Role-Based Access Control and Selective Endpoint Protection

As a **software engineer**,
I want **RBAC to be enforced via reusable route dependencies backed by external-identity claims and optional Graph role lookups**,
So that **I can selectively secure endpoints while keeping protection logic explicit and easy to replicate**.

**Acceptance Criteria:**

**Given** the application defines a central role model
**When** I inspect the implementation
**Then** roles are represented in a shared enum/type
**And** principals carry normalized role claims

**Given** an endpoint protected with authentication-only dependency
**When** I call it with `AUTH_TYPE=entra` and no bearer token
**Then** the response is a 401 with a structured error

**Given** an endpoint protected with role dependency
**When** I call it with an authenticated principal that lacks the required role
**Then** the response is a 403 with a structured error

**Given** graph-role enforcement is enabled
**When** role checks run
**Then** role evaluation combines token roles with externally fetched role assignments for the current user

**Given** an unprotected endpoint
**When** I call it without a token
**Then** the response succeeds normally

**Given** the endpoint protection implementation
**When** I inspect route handlers
**Then** protection is applied explicitly through `Depends()` per endpoint
**And** role checking is reusable through a parameterized dependency factory
**And** adding auth/authz to a new endpoint requires only wiring the appropriate dependency
