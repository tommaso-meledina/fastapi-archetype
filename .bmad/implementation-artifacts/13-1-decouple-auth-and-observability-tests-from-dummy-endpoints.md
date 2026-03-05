# Story 13.1: Decouple Auth and Observability Tests from Dummy Endpoints

Status: ready-for-dev

## Story

As a **software engineer maintaining the archetype**,
I want **auth and observability integration tests to exercise infrastructure capabilities through test-local stub endpoints rather than through the Dummy resource**,
So that **these tests remain valid and passing regardless of which business resources exist in the application**.

## Acceptance Criteria

1. **Given** the auth integration tests in `tests/auth/test_dependencies.py` and `tests/auth/test_entra_integration.py`
   **When** I inspect their implementation
   **Then** they exercise authentication and authorization through lightweight stub routes defined in test fixtures, not through `/v1/dummies` or `/v2/dummies`
   **And** the stub routes replicate the same auth dependency patterns (unauthenticated, `require_auth`, `require_role(Role.ADMIN)`)

2. **Given** the Prometheus integration tests in `tests/observability/test_prometheus.py`
   **When** I inspect their implementation
   **Then** they exercise metric instrumentation through test-local stub endpoints or direct metric assertions, not through `/v1/dummies` or `/v2/dummies`

3. **Given** all auth and observability tests have been decoupled
   **When** I run the full test suite
   **Then** all tests pass with the same coverage as before the change
   **And** no test outside `tests/api/test_dummy_routes.py`, `tests/api/test_v2_dummy_routes.py`, `tests/services/v1/test_dummy_service.py`, and `tests/services/v2/test_dummy_service.py` references the Dummy resource or its endpoints

## Tasks / Subtasks

- [ ] Task 1 — Create test stub routes in `tests/conftest.py` (AC: #1, #2, #3)
  - [ ] 1.1 Add a test router with stub endpoints replicating auth patterns: open GET, `require_auth` POST, `require_role(Role.ADMIN)` POST
  - [ ] 1.2 Add a test router with rate-limited stub endpoints for rate limit tests
  - [ ] 1.3 Register the test router on the app in `tests/conftest.py`
- [ ] Task 2 — Decouple auth tests (AC: #1, #3)
  - [ ] 2.1 Rewrite `tests/auth/test_dependencies.py` to use stub routes instead of `/v1/dummies` and `/v2/dummies`
  - [ ] 2.2 Rewrite `tests/auth/test_entra_integration.py` to use stub routes
  - [ ] 2.3 Rewrite `tests/auth/test_role_mapping.py` to use stub routes
- [ ] Task 3 — Decouple observability tests (AC: #2, #3)
  - [ ] 3.1 Rewrite `tests/observability/test_prometheus.py` to use direct metric assertions only (no dummy imports/endpoints)
  - [ ] 3.2 Rewrite `tests/observability/test_logging.py` trace correlation test to use `/health` or stub instead of `/v1/dummies`
- [ ] Task 4 — Decouple remaining infrastructure tests (AC: #3)
  - [ ] 4.1 Rewrite `tests/core/test_rate_limit.py` to use stub rate-limited routes
  - [ ] 4.2 Rewrite `tests/core/test_errors.py` to remove Dummy references (use generic endpoints/error codes only)
- [ ] Task 5 — Verify full decoupling (AC: #3)
  - [ ] 5.1 Run full test suite and confirm all pass
  - [ ] 5.2 Verify no test outside the four dummy-specific files references Dummy resource or endpoints

## Dev Notes

- **Stub route approach:** Add test-only routes to the FastAPI app at test-import time via `tests/conftest.py`. Use a dedicated `APIRouter(prefix="/test")` with endpoints that replicate auth patterns without involving any business resource.
- **Auth patterns to replicate:** GET (open/no-auth), POST with `Depends(require_auth)`, POST with `Depends(require_role(Role.ADMIN))`
- **Rate limit stubs:** Create rate-limited GET/POST endpoints using `@limiter.limit()` with configurable rate settings
- **Prometheus tests:** Convert to direct `Counter` manipulation and assertions. Remove all imports of `Dummy`, `dummy_service`, and any `/v{n}/dummies` references.
- **Project conventions:** `from __future__ import annotations` at top of every module; type-checking imports guarded by `if TYPE_CHECKING`

### References

- [Source: .bmad/planning-artifacts/epics/epic-13-demo-removal.md#Story 13.1]
- [Source: PROJECT_CONTEXT.md#Testing]
- [Source: PROJECT_CONTEXT.md#Authentication and Authorization]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking (Cursor)

### Debug Log References

### Completion Notes List

### File List
