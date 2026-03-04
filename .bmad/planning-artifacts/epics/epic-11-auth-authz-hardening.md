# Epic 11: Auth/Authz Hardening

Auth subsystem refinements to improve production-readiness: sanitized error responses, validated auth behavior under realistic IdP simulation, and an extensible role-mapping contract for bridging internal role labels to external identity systems.

**FRs covered:** FR39–FR41
**Phase:** 2 (Expansion)

## Story 11.1: Auth Error Response Sanitization

As a **software engineer**,
I want **auth error responses to return consistent, safe messages without leaking provider internals**,
So that **production deployments don't expose discovery URIs, token endpoint details, or stack information to callers**.

**Acceptance Criteria:**

**Given** a bearer token that fails validation for any reason (malformed, expired, bad signature, wrong issuer/audience)
**When** the error response is returned
**Then** the response body uses the standard structured error format with a generic client-facing message
**And** provider-specific failure details are logged server-side but not included in the response `detail` field

**Given** an auth-protected endpoint called without a token
**When** the 401 response is returned
**Then** the `detail` field contains a safe, generic message (e.g., "Authentication required")

**Given** a role-protected endpoint where the principal lacks the required role
**When** the 403 response is returned
**Then** the `detail` field indicates insufficient permissions without revealing which roles were evaluated or how

## Story 11.2: Synthetic IdP Integration Tests

As a **software engineer**,
I want **integration tests that exercise the full `entra` auth code path using a test-generated RSA keypair and monkeypatched HTTP calls**,
So that **bearer-token validation, claim mapping, and role enforcement are verified end-to-end without external infrastructure**.

**Acceptance Criteria:**

**Given** a test RSA keypair and a helper that signs JWTs with controlled claims
**When** the Entra provider's `_http_get` and `_http_post_form` methods are monkeypatched to return matching JWKS and mock responses
**Then** the full `authenticate_bearer_token` path executes against real signature verification logic

**Given** test configuration with `AUTH_TYPE=entra` and matching issuer/audience
**When** a valid signed token is sent to a protected endpoint
**Then** the response is 200 and the principal is correctly populated

**Given** various invalid token scenarios (missing token, expired, wrong issuer, wrong audience, invalid signature)
**When** each is sent to a protected endpoint
**Then** the response is 401 with a sanitized error body (per Story 11.1)

**Given** a valid token with insufficient roles
**When** sent to a role-protected endpoint
**Then** the response is 403

**Given** Graph role enrichment is enabled
**When** a role check executes
**Then** the monkeypatched Graph response is incorporated into role evaluation

## Story 11.3: RoleMappingProvider Abstraction

As a **software engineer**,
I want **role checks to resolve internal role labels to external identifiers through a pluggable mapping provider**,
So that **the archetype supports IdP configurations where roles are represented as GUIDs or other non-human-readable identifiers, without coupling the mapping strategy to the auth subsystem**.

**Acceptance Criteria:**

**Given** a `RoleMappingProvider` ABC
**When** I inspect the contract
**Then** it defines a `to_external(role_name: str) -> str` method (string in, string out — no enum coupling)

**Given** `BasicRoleMappingProvider`
**When** `to_external("admin")` is called
**Then** it returns `"admin"` (identity mapping)

**Given** `require_role` dependency
**When** role enforcement runs
**Then** it calls `role_mapper.to_external(required_role.value)` and checks the result against the principal's roles
**And** the `RoleMappingProvider` is injected via the same settings-driven factory pattern used for `AuthProvider`

**Given** a developer extending the archetype
**When** they implement a custom `RoleMappingProvider` (e.g., env-based or table-based)
**Then** they can wire it in by updating the factory without modifying auth dependencies or route handlers
