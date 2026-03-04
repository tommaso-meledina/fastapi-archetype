# Story 8.1: URL Prefix Versioning with APIRouter

Status: done

## Story

As a **software engineer**,
I want **all business API endpoints organized under a `/v1/` URL prefix using FastAPI's `APIRouter`**,
so that **I have a clear versioning pattern I can replicate when a new API version is needed, and infrastructure endpoints remain version-independent**.

## Acceptance Criteria

1. **Given** the application is running **When** I send `GET /v1/dummies` or `POST /v1/dummies` **Then** the endpoints behave identically to the previous unversioned `/dummies` endpoints.

2. **Given** the application is running **When** I send `GET /dummies` (the old unversioned path) **Then** the response is 404 — the unversioned path no longer exists.

3. **Given** the application is running **When** I access `/health`, `/metrics`, `/docs`, or `/redoc` **Then** these infrastructure endpoints remain at the root level, unversioned.

4. **Given** the versioning implementation **When** I inspect the code **Then** a versioned `APIRouter(prefix="/v1")` groups all business API routes **And** the router is included in the application via `app.include_router()` **And** adding a future `/v2/` version would mean creating a new `APIRouter(prefix="/v2")` — no structural changes to the existing v1.

5. **Given** the Swagger UI at `/docs` **When** I inspect the documented endpoints **Then** all business endpoints show their versioned paths (e.g., `/v1/dummies`) **And** infrastructure endpoints are listed at their root paths.

6. **Given** the existing test suite **When** all tests are updated for the new URL paths **Then** the full test suite passes with the versioned endpoint structure.

## Tasks / Subtasks

- [x] Task 1: Create a v1 versioned router in `src/fastapi_archetype/api/v1/__init__.py` (AC: 4)
  - [x] Create `src/fastapi_archetype/api/v1/` package with `__init__.py`
  - [x] Define `router = APIRouter(prefix="/v1")` in the v1 package `__init__.py`
  - [x] Include `dummy_router` (from `api/dummy_routes.py`) into the v1 router via `router.include_router(dummy_router)`
- [x] Task 2: Update `main.py` to include the v1 router instead of the dummy_router directly (AC: 3, 4)
  - [x] Import the v1 router from `api.v1`
  - [x] Replace `app.include_router(dummy_router)` with `app.include_router(v1_router)`
  - [x] Confirm `/health` remains at root (already registered on `app` directly — no change needed)
  - [x] Confirm `/metrics`, `/docs`, `/redoc` remain at root (no change needed)
- [x] Task 3: Update all test paths from `/dummies` to `/v1/dummies` (AC: 1, 2, 6)
  - [x] Update `tests/api/test_dummy_routes.py` — all `client.get("/dummies")` and `client.post("/dummies", ...)` calls
  - [x] Update `tests/observability/test_prometheus.py` — the `client.post("/dummies", ...)` calls
  - [x] Update `tests/core/test_errors.py` — validation error test path
  - [x] Verify `/health` test still passes unchanged at `/health`
  - [x] Added `test_unversioned_dummies_get_returns_404` and `test_unversioned_dummies_post_returns_404` to verify AC 2
- [x] Task 4: Run quality checks — ruff lint + format, full test suite (AC: all)

## Dev Notes

### Technical Approach

Use FastAPI's nested `APIRouter` pattern. The v1 router acts as a grouping router with `prefix="/v1"`. The existing `dummy_routes.py` router keeps `prefix="/dummies"`. Including `dummy_router` inside `v1_router` produces final paths `/v1/dummies`.

The key files are:
- **New**: `src/fastapi_archetype/api/v1/__init__.py` — v1 router definition
- **Modified**: `src/fastapi_archetype/main.py` — include v1 router instead of dummy_router
- **Modified**: `tests/api/test_dummy_routes.py` — update all endpoint paths
- **Modified**: `tests/observability/test_prometheus.py` — update `/dummies` paths

### Architecture Compliance

- Business routes go under `api/v1/` — the `api/` boundary principle is preserved [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Architectural Boundaries]
- Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at the root level — they are NOT business API routes [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR38]
- `dummy_routes.py` stays in `api/` (not moved into `api/v1/`); the v1 `__init__.py` includes it. This preserves the existing module layout while adding the version prefix
- No new dependencies — this uses only FastAPI's built-in `APIRouter`

### Constants

- `DUMMIES.path` remains `"/dummies"` — no change. The `/v1` prefix comes from the v1 router, not the resource constant
- `HEALTH_PATH` remains `"/health"` — no change

### Anti-Patterns to Avoid

- Do NOT move `dummy_routes.py` into `api/v1/` — keep it where it is and include it via the v1 router
- Do NOT change `DUMMIES.path` to include `/v1` — the version prefix is the router's concern, not the resource definition
- Do NOT create a separate `api/v1/dummy_routes.py` — reuse the existing route module
- Do NOT add version prefixes to `/health`, `/metrics`, `/docs`, or `/redoc`
- Do NOT introduce any new libraries or dependencies

### Testing Strategy

- Update all URL paths in tests from `/dummies` to `/v1/dummies`
- The `/health` test at `tests/api/test_health.py` should remain unchanged — it tests `/health` at the root
- The Prometheus test that sends POST to `/dummies` must be updated to `/v1/dummies`
- The `/metrics` endpoint path remains `/metrics` (no change)
- Verify that `GET /dummies` returns 404 (add one test for this)

### Previous Story Intelligence (Story 7.1)

- Story 7.1 added `DUMMIES_CREATED_TOTAL` counter in `observability/prometheus.py` and increments it in `services/dummy_service.py`
- The Prometheus tests in `tests/observability/test_prometheus.py` use `client.post("/dummies", ...)` — these paths must be updated to `/v1/dummies`
- 46 tests existed after Story 7.1; all must continue to pass

### Git Patterns

- Recent commits follow: `feat:` for new features, `fix:` for corrections, `chore:` for housekeeping
- Conventional Commits standard is used throughout

### References

- [Source: .bmad/planning-artifacts/epics/epic-8-api-versioning.md#Story 8.1]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR37, FR38]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Created `api/v1/__init__.py` with `APIRouter(prefix="/v1")` that includes `dummy_router` — nested router pattern produces `/v1/dummies` paths
- Updated `main.py` to import and include `v1_router` instead of `dummy_router` directly
- Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at root — untouched
- Updated all test files: `test_dummy_routes.py`, `test_prometheus.py`, `test_errors.py` to use `/v1/dummies` paths
- Added `test_unversioned_dummies_get_returns_404` and `test_unversioned_dummies_post_returns_404` to verify old `/dummies` path returns 404 for both methods (AC 2)
- No new dependencies — uses only FastAPI's built-in `APIRouter`
- All 48 tests pass (2 new + 46 existing), zero regressions
- Ruff lint and format pass
- Code review: fixed MEDIUM finding (missing POST 404 test for unversioned path)

### Change Log

- 2026-03-04: Implemented URL prefix versioning with APIRouter (Story 8.1) — business endpoints moved to `/v1/` prefix

### File List

- src/fastapi_archetype/api/v1/__init__.py (created — v1 router with prefix="/v1", includes dummy_router)
- src/fastapi_archetype/main.py (modified — import v1_router instead of dummy_router)
- tests/api/test_dummy_routes.py (modified — all paths updated to /v1/dummies, added 404 test)
- tests/observability/test_prometheus.py (modified — paths updated to /v1/dummies)
- tests/core/test_errors.py (modified — validation error test path updated to /v1/dummies)
