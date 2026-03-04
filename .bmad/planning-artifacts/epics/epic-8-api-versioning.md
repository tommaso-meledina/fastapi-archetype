# Epic 8: API Versioning

A developer can see that all business API endpoints are organized under a versioned URL prefix (`/v1/`), while infrastructure endpoints remain at the root — providing a clear, framework-native pattern for introducing future API versions without breaking existing clients.

## Story 8.1: URL Prefix Versioning with APIRouter

As a **software engineer**,
I want **all business API endpoints organized under a `/v1/` URL prefix using FastAPI's `APIRouter`**,
So that **I have a clear versioning pattern I can replicate when a new API version is needed, and infrastructure endpoints remain version-independent**.

**Acceptance Criteria:**

**Given** the application is running
**When** I send `GET /v1/dummies` or `POST /v1/dummies`
**Then** the endpoints behave identically to the previous unversioned `/dummies` endpoints

**Given** the application is running
**When** I send `GET /dummies` (the old unversioned path)
**Then** the response is 404 — the unversioned path no longer exists

**Given** the application is running
**When** I access `/health`, `/metrics`, `/docs`, or `/redoc`
**Then** these infrastructure endpoints remain at the root level, unversioned

**Given** the versioning implementation
**When** I inspect the code
**Then** a versioned `APIRouter(prefix="/v1")` groups all business API routes
**And** the router is included in the application via `app.include_router()`
**And** adding a future `/v2/` version would mean creating a new `APIRouter(prefix="/v2")` — no structural changes to the existing v1

**Given** the Swagger UI at `/docs`
**When** I inspect the documented endpoints
**Then** all business endpoints show their versioned paths (e.g., `/v1/dummies`)
**And** infrastructure endpoints are listed at their root paths

**Given** the existing test suite
**When** all tests are updated for the new URL paths
**Then** the full test suite passes with the versioned endpoint structure
