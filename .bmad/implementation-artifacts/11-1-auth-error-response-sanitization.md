# Story 11.1: Auth Error Response Sanitization

Status: done

## Story

As a **software engineer**,
I want **auth error responses to return consistent, safe messages without leaking provider internals**,
so that **production deployments don't expose discovery URIs, token endpoint details, or stack information to callers**.

## Acceptance Criteria

1. **Given** a bearer token that fails validation for any reason (malformed, expired, bad signature, wrong issuer/audience), **When** the error response is returned, **Then** the response body uses the standard structured error format with a generic client-facing message, **And** provider-specific failure details are logged server-side but not included in the response `detail` field.

2. **Given** an auth-protected endpoint called without a token, **When** the 401 response is returned, **Then** the `detail` field contains a safe, generic message (e.g., "Authentication required").

3. **Given** a role-protected endpoint where the principal lacks the required role, **When** the 403 response is returned, **Then** the `detail` field indicates insufficient permissions without revealing which roles were evaluated or how.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 2) Sanitize 401 responses in `get_current_principal`
  - [x] 1.1 Add a module-level logger to `dependencies.py` via `logging.getLogger(__name__)`
  - [x] 1.2 In `get_current_principal`, log the provider-specific exception detail at WARNING level before raising
  - [x] 1.3 Replace `detail=str(exc)` with `detail=None` on all `AppException(ErrorCode.UNAUTHORIZED, ...)` raises so the response uses the generic `ErrorCode.UNAUTHORIZED` message ("Authentication required") only
  - [x] 1.4 For the missing-token case, use `detail=None` (the ErrorCode message is already correct)
- [x] Task 2 (AC: 3) Sanitize 403 responses in `require_role`
  - [x] 2.1 In the `require_role` closure, log the specific missing role at WARNING level
  - [x] 2.2 Replace `detail=f"Missing required role: ..."` with `detail=None` so the response uses the generic `ErrorCode.FORBIDDEN` message ("Access forbidden") only
- [x] Task 3 (AC: 1, 2, 3) Add/update tests
  - [x] 3.1 Add test: 401 for malformed token does not leak provider error text (response detail is null)
  - [x] 3.2 Add test: 401 for missing token returns generic message without internals
  - [x] 3.3 Add test: 403 for insufficient role does not reveal the required role name
  - [x] 3.4 Add test: provider-specific error is logged at WARNING level (use caplog)
  - [x] 3.5 Verify all existing auth tests still pass (no regressions)

## Dev Notes

### Architecture Compliance

- Error codes remain in `core/errors.py` — no new codes needed
- Logger uses `logging.getLogger(__name__)` per project convention
- Tests in `tests/auth/` mirroring source structure

### References

- [Source: src/fastapi_archetype/auth/dependencies.py]
- [Source: src/fastapi_archetype/core/errors.py]
- [Source: .bmad/planning-artifacts/epics/epic-11-auth-authz-hardening.md#Story 11.1]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking

### Debug Log References

### Completion Notes List

- Sanitized all auth error responses: `detail=str(exc)` replaced with `detail=None` across `get_current_principal` and `require_role`
- Added `logger = logging.getLogger(__name__)` at module level
- Provider-specific errors now logged at WARNING before re-raising as generic AppException
- 6 new tests verify sanitization: 4 for 401 paths, 2 for 403 path
- All 84 tests pass with no regressions

### File List

- `src/fastapi_archetype/auth/dependencies.py` (modified)
- `tests/auth/test_dependencies.py` (new)
