# Story 11.2: Synthetic IdP Integration Tests

Status: done

## Story

As a **software engineer**,
I want **integration tests that exercise the full `entra` auth code path using a test-generated RSA keypair and monkeypatched HTTP calls**,
so that **bearer-token validation, claim mapping, and role enforcement are verified end-to-end without external infrastructure**.

## Acceptance Criteria

1. **Given** a test RSA keypair and a helper that signs JWTs with controlled claims, **When** the Entra provider's `_http_get` and `_http_post_form` methods are monkeypatched to return matching JWKS and mock responses, **Then** the full `authenticate_bearer_token` path executes against real signature verification logic.

2. **Given** test configuration with `AUTH_TYPE=entra` and matching issuer/audience, **When** a valid signed token is sent to a protected endpoint, **Then** the response is 200 and the principal is correctly populated.

3. **Given** various invalid token scenarios (missing token, expired, wrong issuer, wrong audience, invalid signature), **When** each is sent to a protected endpoint, **Then** the response is 401 with a sanitized error body (per Story 11.1).

4. **Given** a valid token with insufficient roles, **When** sent to a role-protected endpoint, **Then** the response is 403.

5. **Given** Graph role enrichment is enabled, **When** a role check executes, **Then** the monkeypatched Graph response is incorporated into role evaluation.

## Tasks / Subtasks

- [x] Task 1 (AC: 1) Create test RSA keypair infrastructure and JWT helpers
  - [x] 1.1 Create `tests/auth/conftest.py` with module-scoped RSA keypair fixture
  - [x] 1.2 Create `sign_jwt` helper fixture
  - [x] 1.3 Create `jwks_response` fixture
  - [x] 1.4 Create `entra_settings` fixture (via `_entra_settings` helper)
- [x] Task 2 (AC: 1, 2) Create monkeypatched Entra provider and valid token tests
  - [x] 2.1 Create fixture with monkeypatched `_http_get` and `_http_post_form`
  - [x] 2.2 Test: valid token returns correctly populated Principal
  - [x] 2.3 Test: valid token on protected endpoint returns 201
- [x] Task 3 (AC: 3) Test invalid token scenarios
  - [x] 3.1 Test: missing token → 401
  - [x] 3.2 Test: expired token → 401
  - [x] 3.3 Test: wrong issuer → 401
  - [x] 3.4 Test: wrong audience → 401
  - [x] 3.5 Test: invalid signature → 401
  - [x] 3.6 All 401 responses verified to have sanitized detail (null)
- [x] Task 4 (AC: 4) Test role enforcement
  - [x] 4.1 Test: reader only → 403 on admin endpoint
  - [x] 4.2 Test: admin role → 201 on admin endpoint
- [x] Task 5 (AC: 5) Test Graph role enrichment
  - [x] 5.1 Created `graph_enrichment_client` fixture with Graph API mock
  - [x] 5.2 Test: no direct roles + Graph returns admin → 201
- [x] Task 6 Full regression: 100 tests pass

## Dev Notes

### Architecture Compliance

- Uses `PyJWT` and `cryptography` — both already in dependency tree, no new deps
- Tests in `tests/auth/` mirroring source structure
- Provider-level tests (TestProviderLevelValidation) + endpoint integration tests (TestEndpointIntegration)

### References

- [Source: src/fastapi_archetype/auth/providers/entra.py]
- [Source: tests/auth/conftest.py]
- [Source: tests/auth/test_entra_integration.py]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking

### Debug Log References

### Completion Notes List

- Created `tests/auth/conftest.py` with RSA keypair, JWKS, and sign_jwt fixtures
- Created `tests/auth/test_entra_integration.py` with 16 tests across 4 test classes
- TestProviderLevelValidation: 6 tests exercising authenticate_bearer_token directly
- TestEndpointIntegration: 7 tests exercising full HTTP request/response cycle
- TestRoleEnforcement: 2 tests for RBAC with synthetic tokens
- TestGraphRoleEnrichment: 1 test for Graph API role enrichment path
- All 100 tests pass, zero regressions

### File List

- `tests/auth/conftest.py` (new)
- `tests/auth/test_entra_integration.py` (new)
