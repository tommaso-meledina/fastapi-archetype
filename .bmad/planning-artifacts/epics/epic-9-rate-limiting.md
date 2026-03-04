# Epic 9: Rate Limiting

A developer can see per-endpoint rate limiting enforced on the API, with limits configurable via environment variables, standard rate-limit response headers, and a clear 429 error response — serving as a production-ready pattern for protecting any service scaffolded from this archetype.

**New library required:** `slowapi` — the de facto rate limiting library for FastAPI, built on `limits`, inspired by Flask-Limiter. Integrates with FastAPI's `Request` object and supports per-endpoint decorators.

## Story 9.1: Per-Endpoint Rate Limiting with Environment Configuration

As a **software engineer**,
I want **per-endpoint rate limits enforced on API requests, with thresholds configurable through environment variables**,
So that **I can protect endpoints from abuse with limits tuned per environment, without code changes**.

**Acceptance Criteria:**

**Given** the application is running with default rate limit configuration
**When** I send requests to a rate-limited endpoint within the allowed threshold
**Then** the responses include standard rate-limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
**And** the response status is the normal success code

**Given** the application is running
**When** I exceed the configured rate limit for an endpoint
**Then** the response status is 429 (Too Many Requests)
**And** the response body follows the application's structured error format (`errorCode`, `message`, `detail`)
**And** rate-limit headers indicate the limit has been reached

**Given** `AppSettings` defines rate limit configuration values
**When** I set rate limit environment variables (e.g., `RATE_LIMIT_GET_DUMMIES`, `RATE_LIMIT_POST_DUMMIES`)
**Then** the application uses those values as the per-endpoint thresholds
**And** sensible defaults are provided when variables are not set

**Given** the rate limiting implementation
**When** I inspect the code
**Then** `slowapi` is used with per-endpoint `@limiter.limit()` decorators
**And** limit strings are read from `AppSettings`, not hardcoded
**And** the pattern is clear enough to replicate for new endpoints

**Given** the rate limiting configuration
**When** I inspect `.env.example`
**Then** all rate limit environment variables are documented with their default values and format (e.g., `100/minute`)
