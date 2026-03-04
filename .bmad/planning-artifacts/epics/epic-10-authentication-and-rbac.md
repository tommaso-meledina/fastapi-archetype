# Epic 10: Authentication and Role-Based Access Control

A developer can see JWT-based authentication and role-based access control (RBAC) integrated into the application using FastAPI's built-in security utilities — with selective endpoint protection via dependency injection and a replicable pattern for securing any service scaffolded from this archetype.

**New libraries required:**
- `python-jose[cryptography]` — JWT encoding/decoding (used in FastAPI's official security tutorial)
- `passlib[bcrypt]` — password hashing (used in FastAPI's official security tutorial)

## Story 10.1: JWT Authentication Infrastructure

As a **software engineer**,
I want **a JWT-based authentication flow using FastAPI's built-in OAuth2 utilities**,
So that **I have a working, standard authentication pattern I can adapt for any service, with token-based security that integrates with Swagger UI's Authorize button**.

**Acceptance Criteria:**

**Given** the application is running
**When** I send a `POST` to the token endpoint with valid credentials
**Then** the response contains a JWT access token
**And** the token includes user identity and role claims

**Given** the application is running
**When** I send a `POST` to the token endpoint with invalid credentials
**Then** the response is a 401 with a structured error following the application's error format

**Given** `AppSettings` defines authentication configuration
**When** I inspect the settings
**Then** JWT secret key, algorithm, and token expiry are configurable via environment variables
**And** sensible defaults are provided for development

**Given** the authentication implementation
**When** I inspect the code
**Then** it uses `fastapi.security.OAuth2PasswordBearer` for token extraction
**And** it uses `python-jose` for JWT encoding/decoding
**And** it uses `passlib` for password hashing
**And** the pattern follows FastAPI's official security tutorial structure

**Given** the Swagger UI at `/docs`
**When** I click the "Authorize" button
**Then** I can authenticate using the OAuth2 Password flow and subsequent requests include the token automatically

## Story 10.2: Role-Based Access Control and Selective Endpoint Protection

As a **software engineer**,
I want **role-based access control that allows selective protection of individual endpoints via FastAPI's dependency injection**,
So that **I can control which endpoints require authentication and which roles are authorized, using a pattern I can replicate for new endpoints**.

**Acceptance Criteria:**

**Given** the application defines user roles
**When** I inspect the implementation
**Then** roles are represented as an enum or similar structure in a central location
**And** user records include a role assignment

**Given** a protected endpoint (e.g., `POST /dummies`)
**When** I send a request without a valid JWT token
**Then** the response is a 401 with a structured error

**Given** a protected endpoint requiring a specific role
**When** I send a request with a valid JWT token but insufficient role
**Then** the response is a 403 with a structured error

**Given** an unprotected endpoint (e.g., `GET /dummies`)
**When** I send a request without a token
**Then** the response succeeds normally — no authentication required

**Given** the endpoint protection implementation
**When** I inspect the code
**Then** protection is applied via `Depends()` on individual route handlers
**And** the role-check dependency is reusable and accepts the required role as a parameter
**And** the pattern is clear enough to replicate: adding protection to a new endpoint requires only adding a `Depends()` parameter

**Given** the application
**When** I inspect which endpoints are protected
**Then** at least one endpoint demonstrates authentication-only protection
**And** at least one endpoint demonstrates role-based protection
**And** at least one endpoint remains fully open
