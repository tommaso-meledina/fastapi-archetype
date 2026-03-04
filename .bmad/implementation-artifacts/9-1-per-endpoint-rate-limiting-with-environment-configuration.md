# Story 9.1: Per-Endpoint Rate Limiting with Environment Configuration

Status: review

## Story

As a **software engineer**,
I want **per-endpoint rate limits enforced on API requests, with thresholds configurable through environment variables**,
so that **I can protect endpoints from abuse with limits tuned per environment, without code changes**.

## Acceptance Criteria

1. **Given** the application is running with default rate limit configuration **When** I send requests to a rate-limited endpoint within the allowed threshold **Then** the responses include standard rate-limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) **And** the response status is the normal success code.

2. **Given** the application is running **When** I exceed the configured rate limit for an endpoint **Then** the response status is 429 (Too Many Requests) **And** the response body follows the application's structured error format (`errorCode`, `message`, `detail`) **And** rate-limit headers indicate the limit has been reached.

3. **Given** `AppSettings` defines rate limit configuration values **When** I set rate limit environment variables (e.g., `RATE_LIMIT_GET_DUMMIES`, `RATE_LIMIT_POST_DUMMIES`) **Then** the application uses those values as the per-endpoint thresholds **And** sensible defaults are provided when variables are not set.

4. **Given** the rate limiting implementation **When** I inspect the code **Then** `slowapi` is used with per-endpoint `@limiter.limit()` decorators **And** limit strings are read from `AppSettings`, not hardcoded **And** the pattern is clear enough to replicate for new endpoints.

5. **Given** the rate limiting configuration **When** I inspect `.env.example` **Then** all rate limit environment variables are documented with their default values and format (e.g., `100/minute`).

## Tasks / Subtasks

- [x] Task 1: Add `slowapi` dependency (AC: 4)
  - [x] Add `slowapi>=0.1.9` to `pyproject.toml` dependencies
  - [x] Run `uv sync` to install
- [x] Task 2: Add rate limit settings to `AppSettings` (AC: 3)
  - [x] Add `rate_limit_default`, `rate_limit_get_dummies`, `rate_limit_post_dummies` fields with sensible defaults (e.g., `100/minute`)
  - [x] Document variables in `.env.example`
- [x] Task 3: Add `RATE_LIMITED` error code to `ErrorCode` enum (AC: 2)
  - [x] Add `RATE_LIMITED = ("RATE_LIMITED", "Rate limit exceeded", 429)` to `ErrorCode`
  - [x] Create `rate_limit_exceeded_handler` that returns the structured error format
- [x] Task 4: Create limiter instance and integrate with FastAPI app (AC: 1, 4)
  - [x] Create `src/fastapi_archetype/core/rate_limit.py` with `Limiter` instance using `get_remote_address` as key function
  - [x] Attach limiter to `app.state` in `main.py`
  - [x] Register the custom `RateLimitExceeded` exception handler in `main.py`
- [x] Task 5: Apply rate limit decorators to v1 and v2 endpoints (AC: 1, 4)
  - [x] Decorate `list_dummies` in v1 and v2 with `@limiter.limit()` reading from settings
  - [x] Decorate `create_dummy` in v1 and v2 with `@limiter.limit()` reading from settings
  - [x] Ensure `Request` and `Response` parameters are available in each endpoint signature (required by slowapi for enforcement and header injection)
- [x] Task 6: Write tests for rate limiting behavior (AC: 1, 2, 3)
  - [x] Test that successful responses include rate-limit headers
  - [x] Test that exceeding the limit returns 429 with structured error body
  - [x] Test that remaining header decrements on successive requests
- [x] Task 7: Run quality checks — ruff lint + format, full test suite (AC: all)

## Dev Notes

### Technical Approach

Use `slowapi` (v0.1.9), the de facto rate limiting library for FastAPI/Starlette. It wraps the `limits` library and provides per-endpoint `@limiter.limit()` decorators.

Key implementation pattern:
1. Create a `Limiter` instance with `key_func=get_remote_address` in a dedicated `core/rate_limit.py` module
2. Attach `limiter` to `app.state.limiter` in `main.py`
3. Register a **custom** `RateLimitExceeded` handler that returns the project's structured error format (NOT slowapi's default handler)
4. Apply `@limiter.limit(settings.rate_limit_xxx)` decorators on each endpoint, reading limit strings from `AppSettings`

slowapi requires that every rate-limited endpoint has a `request: Request` parameter. Since the current endpoints don't have one, add it as a parameter.

### Architecture Compliance

- Rate limiting is a **cross-cutting concern** — the limiter module belongs in `core/` [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- Error response format MUST use the existing `_build_error_body` function from `core/errors.py` — `errorCode: "RATE_LIMITED"`, `message`, `detail` [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Format Patterns]
- Configuration goes in `AppSettings` via pydantic-settings with env var support [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#API & Communication Patterns]
- All constants and error codes in their respective `core/` modules [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Enforcement Guidelines]

### File Structure

- **New**: `src/fastapi_archetype/core/rate_limit.py` — limiter instance creation
- **Modified**: `src/fastapi_archetype/core/config.py` — rate limit settings fields
- **Modified**: `src/fastapi_archetype/core/errors.py` — `RATE_LIMITED` error code + handler
- **Modified**: `src/fastapi_archetype/main.py` — attach limiter to app, register exception handler
- **Modified**: `src/fastapi_archetype/api/v1/dummy_routes.py` — add `@limiter.limit()` decorators + `request: Request` param
- **Modified**: `src/fastapi_archetype/api/v2/dummy_routes.py` — same as v1
- **Modified**: `.env.example` — document rate limit variables
- **New**: `tests/core/test_rate_limit.py` — rate limiting tests

### Anti-Patterns to Avoid

- Do NOT use slowapi's default `_rate_limit_exceeded_handler` — it does not return the project's structured error format
- Do NOT hardcode rate limit strings in decorators — always read from `AppSettings`
- Do NOT create the `Limiter` inside `main.py` — keep it in `core/rate_limit.py` for separation
- Do NOT forget the `request: Request` parameter on rate-limited endpoints — slowapi requires it
- Do NOT apply rate limits to `/health` or `/metrics` — those are infrastructure endpoints

### Testing Strategy

- Use a very low rate limit (e.g., `2/minute`) in tests to easily trigger 429
- Override settings in test fixtures to set low thresholds
- Test that response headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` are present
- Test that 429 body matches `{"errorCode": "RATE_LIMITED", "message": "Rate limit exceeded", "detail": ...}`
- Ensure all existing tests still pass (no regressions)

### Previous Story Intelligence (Story 8.1)

- Story 8.1 established the v1/v2 routing pattern — endpoints are at `/v1/dummies` and `/v2/dummies`
- Both v1 and v2 share the same route structure, both need rate limiting applied
- 48 existing tests must continue to pass
- Conventional Commits standard: `feat:` for new features

### Library Specifics (slowapi 0.1.9)

- `from slowapi import Limiter`
- `from slowapi.util import get_remote_address`
- `from slowapi.errors import RateLimitExceeded`
- Limiter key_func identifies the client (IP address by default)
- Limit strings use the `limits` library format: `"100/minute"`, `"10/second"`, `"5000/hour"`
- The limiter must be attached to `app.state.limiter` for middleware to find it

### References

- [Source: .bmad/planning-artifacts/epics/epic-9-rate-limiting.md#Story 9.1]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Deferred Decisions]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `slowapi>=0.1.9` dependency and installed via `uv sync`
- Added `rate_limit_default`, `rate_limit_get_dummies`, `rate_limit_post_dummies` to `AppSettings` with sensible defaults
- Added `RATE_LIMITED` error code (429) and custom `rate_limit_exceeded_handler` returning structured error format
- Created `core/rate_limit.py` with `Limiter(key_func=get_remote_address, headers_enabled=True)`
- Attached limiter to `app.state` and registered `RateLimitExceeded` handler in `main.py`
- Applied `@limiter.limit()` decorators reading from settings on all v1 and v2 endpoints
- Added `request: Request` and `response: Response` params to endpoints (required by slowapi for enforcement + header injection)
- Added `limiter.reset()` in test conftest to prevent rate limit state from leaking between tests
- 7 new tests covering: headers on success, 429 on exceed, error body structure, v2 headers, health not limited, remaining decrement
- All 68 tests pass (7 new + 61 existing), zero regressions
- Ruff lint and format pass

### Change Log

- 2026-03-04: Implemented per-endpoint rate limiting with slowapi (Story 9.1) — configurable via env vars, structured 429 response, rate-limit headers on all responses

### File List

- pyproject.toml (modified — added slowapi>=0.1.9 dependency)
- src/fastapi_archetype/core/rate_limit.py (created — Limiter instance with get_remote_address key_func)
- src/fastapi_archetype/core/config.py (modified — added rate_limit_default, rate_limit_get_dummies, rate_limit_post_dummies settings)
- src/fastapi_archetype/core/errors.py (modified — added RATE_LIMITED error code and rate_limit_exceeded_handler)
- src/fastapi_archetype/main.py (modified — attached limiter to app.state, registered RateLimitExceeded handler)
- src/fastapi_archetype/api/v1/dummy_routes.py (modified — added @limiter.limit() decorators, request/response params)
- src/fastapi_archetype/api/v2/dummy_routes.py (modified — added @limiter.limit() decorators, request/response params)
- .env.example (modified — documented rate limit env variables)
- tests/conftest.py (modified — added limiter.reset() to client fixture)
- tests/core/test_rate_limit.py (created — 7 rate limiting tests)
