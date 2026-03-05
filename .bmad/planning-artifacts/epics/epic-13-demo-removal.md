# Epic 13: Demo Removal

A developer who has cloned the archetype and is ready to build their own service can run a single command (`python3 scripts/remove_demo.py`) to strip all Dummy CRUD boilerplate from the project — leaving a clean codebase with all infrastructure, cross-cutting concerns, and structural scaffolding intact, all tests passing, and the application starting successfully. The script lives in a `scripts/` directory at the project root, outside `src/` — it is a development tool, not part of the application code.

**Prerequisite:** Auth and observability tests must be decoupled from specific resource endpoints before the removal script can guarantee a green test suite post-cleanup (Story 13.1).

## Story 13.1: Decouple Auth and Observability Tests from Dummy Endpoints

As a **software engineer maintaining the archetype**,
I want **auth and observability integration tests to exercise infrastructure capabilities through test-local stub endpoints rather than through the Dummy resource**,
So that **these tests remain valid and passing regardless of which business resources exist in the application**.

**Acceptance Criteria:**

**Given** the auth integration tests in `tests/auth/test_dependencies.py` and `tests/auth/test_entra_integration.py`
**When** I inspect their implementation
**Then** they exercise authentication and authorization through lightweight stub routes defined in test fixtures, not through `/v1/dummies` or `/v2/dummies`
**And** the stub routes replicate the same auth dependency patterns (unauthenticated, `require_auth`, `require_role(Role.ADMIN)`)

**Given** the Prometheus integration tests in `tests/observability/test_prometheus.py`
**When** I inspect their implementation
**Then** they exercise metric instrumentation through test-local stub endpoints or direct metric assertions, not through `/v1/dummies` or `/v2/dummies`

**Given** all auth and observability tests have been decoupled
**When** I run the full test suite
**Then** all tests pass with the same coverage as before the change
**And** no test outside `tests/api/test_dummy_routes.py`, `tests/api/test_v2_dummy_routes.py`, `tests/services/v1/test_dummy_service.py`, and `tests/services/v2/test_dummy_service.py` references the Dummy resource or its endpoints

## Story 13.2: Demo Removal Script

As a **software engineer creating a new service from the archetype**,
I want **to run `python3 scripts/remove_demo.py` and have all Dummy CRUD boilerplate removed automatically**,
So that **I start with a clean project that has all infrastructure intact, structural scaffolding in place, and all tests passing — without manually hunting for demo code across the codebase**.

**Acceptance Criteria:**

**Given** the git working tree has uncommitted changes
**When** I run `python3 scripts/remove_demo.py`
**Then** the script prints an informative error message indicating the working tree must be clean
**And** the script exits with a non-zero exit code without modifying any files

**Given** the git working tree is clean
**When** I run `python3 scripts/remove_demo.py`
**Then** the following files are deleted:
- `src/fastapi_archetype/models/dummy.py`
- `src/fastapi_archetype/api/v1/dummy_routes.py`
- `src/fastapi_archetype/api/v2/dummy_routes.py`
- `src/fastapi_archetype/services/v1/dummy_service.py`
- `src/fastapi_archetype/services/v2/dummy_service.py`
- `tests/api/test_dummy_routes.py`
- `tests/api/test_v2_dummy_routes.py`
- `tests/services/v1/test_dummy_service.py`
- `tests/services/v2/test_dummy_service.py`

**Given** the script has executed successfully
**When** I inspect the surgically edited shared files
**Then** `core/constants.py` no longer contains the `DUMMIES` `ResourceDefinition`
**And** `core/errors.py` no longer contains `DUMMY_NOT_FOUND` in the `ErrorCode` enum
**And** `core/config.py` no longer contains `rate_limit_get_dummies` or `rate_limit_post_dummies` fields
**And** `services/__init__.py` no longer imports or applies AOP logging to Dummy service modules
**And** `api/v1/__init__.py` no longer imports or includes the Dummy router
**And** `api/v2/__init__.py` no longer imports or includes the Dummy router
**And** `observability/prometheus.py` no longer contains the `dummies_created_total` counter
**And** `.env.example` no longer contains `RATE_LIMIT_GET_DUMMIES` or `RATE_LIMIT_POST_DUMMIES`
**And** all edited files remain syntactically valid Python (or valid dotenv)

**Given** the script has executed successfully
**When** I inspect the version directories
**Then** `src/fastapi_archetype/api/v1/`, `src/fastapi_archetype/api/v2/`, `src/fastapi_archetype/services/v1/`, and `src/fastapi_archetype/services/v2/` still exist
**And** each contains a valid `__init__.py`

**Given** the script has executed successfully
**When** I start the application (`uvicorn fastapi_archetype.main:app`)
**Then** the application starts without errors
**And** `/health`, `/metrics`, `/docs`, and `/redoc` are reachable and functional

**Given** the script has executed successfully
**When** I run the full test suite (`pytest`)
**Then** all remaining tests pass

**Given** the script implementation
**When** I inspect `scripts/remove_demo.py`
**Then** it is a single Python 3 file with no dependencies beyond the standard library
**And** it uses only `subprocess`, `pathlib`, `os`, or similar stdlib modules for git checks and file operations

**Implementation note for agents:** Testing this feature involves deleting files. Agents must ensure the git working tree is clean before each test run, execute the script, verify the result, and reset from a clean slate after each attempt. Never leave the project in a partially cleaned state.
