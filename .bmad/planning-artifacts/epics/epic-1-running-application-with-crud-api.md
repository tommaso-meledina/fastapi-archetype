# Epic 1: Running Application with CRUD API

A developer can clone the project, run it immediately (SQLite in-memory by default), and interact with a fully working REST API — with structured error responses, centralized constants, auto-generated API docs at `/docs`, and a clear project structure that serves as a copy-and-adapt template. MariaDB is supported via a configuration toggle.

## Story 1.1: Project Initialization and Package Structure

As a **software engineer**,
I want **a cleanly initialized Python 3.14 / FastAPI project with a fully defined package structure and linting configuration**,
So that **I have a runnable project skeleton where every module has a clear home and code style is enforced from the start**.

**Acceptance Criteria:**

**Given** the project is initialized with `uv init`
**When** I inspect the project root
**Then** `pyproject.toml` exists with `requires-python = ">=3.14"`, project name `fastapi-archetype`, and FastAPI + Uvicorn as dependencies
**And** `.python-version` is pinned to `3.14`
**And** `uv.lock` is generated for reproducible dependency resolution

**Given** the project skeleton exists
**When** I inspect the source directory
**Then** the `src/fastapi_archetype/` package exists with `__init__.py`
**And** subpackages exist: `core/`, `models/`, `api/`, `services/`, `aop/`, `observability/` — each with `__init__.py`
**And** a `tests/` directory exists at project root with `__init__.py`

**Given** `src/fastapi_archetype/main.py` exists
**When** I run the application with `uv run uvicorn fastapi_archetype.main:app`
**Then** a FastAPI application starts and responds to HTTP requests
**And** Swagger UI is accessible at `/docs`

**Given** Ruff is configured in `pyproject.toml`
**When** I run `uv run ruff check` and `uv run ruff format --check`
**Then** the entire codebase passes linting and formatting with zero violations

**Given** the project root
**When** I inspect the files
**Then** `.gitignore` exists with appropriate Python/uv exclusions
**And** no dead code, commented-out blocks, or placeholder implementations exist

## Story 1.2: Configuration Management

As a **software engineer**,
I want **typed configuration that loads from a `.env` file and validates all required values at startup**,
So that **misconfiguration is caught immediately rather than at runtime, and I have a clear template of what values are needed**.

**Acceptance Criteria:**

**Given** `core/config.py` defines an `AppSettings` class extending pydantic-settings `BaseSettings`
**When** the application starts with a valid `.env` file
**Then** all configuration values are loaded, typed, and accessible via the settings instance
**And** the settings class reads from the `.env` file automatically

**Given** a `.env` file is missing a required configuration value
**When** the application attempts to start
**Then** it fails fast with a clear validation error before any I/O or database connections are attempted

**Given** the project root
**When** I inspect the files
**Then** `.env.example` exists documenting all required and optional configuration values with descriptions
**And** all configuration values either have sensible defaults or are clearly marked as required

**Given** the configuration includes database connection parameters
**When** the settings are loaded
**Then** a database URL can be constructed from the typed config values for use by the database layer

## Story 1.3: Centralized Constants and Error Handling

As a **software engineer**,
I want **all constants, error codes, and messages defined in central locations with a reusable exception handling framework**,
So that **I never scatter string literals through the codebase and every error response follows a consistent, structured format**.

**Acceptance Criteria:**

**Given** `core/constants.py` exists
**When** I inspect its contents
**Then** resource paths, configuration keys, and shared constants are defined as module-level constants using `UPPER_SNAKE_CASE`
**And** resource definitions are organized as structured objects grouping related constants (path, name, description) per REST resource

**Given** `core/errors.py` exists
**When** I inspect its contents
**Then** an `ErrorCode` enum defines all application error codes
**And** each `ErrorCode` member is paired with a human-readable message
**And** an `AppException` class exists that accepts an `ErrorCode` and optional detail context

**Given** the global exception handler is registered in `main.py`
**When** an `AppException` is raised during request processing
**Then** the response has the appropriate HTTP status code
**And** the response body contains `errorCode` (string), `message` (string), and `detail` (string or null) in camelCase JSON format

**Given** a request triggers a FastAPI validation error (422)
**When** the error response is returned
**Then** it follows the same structured error response format with an application-specific error code

## Story 1.4: Database Layer and Dummy Model

As a **software engineer**,
I want **a database connection layer using SQLModel with a Dummy entity that serves as the reference model**,
So that **I can see exactly how ORM, validation, and database session management are wired together and replicate the pattern for new entities**.

**Acceptance Criteria:**

**Given** `core/database.py` exists
**When** the application starts with valid database configuration
**Then** a SQLAlchemy engine is created using the database URL from `AppSettings` with PyMySQL as the driver
**And** a session generator function provides database sessions via FastAPI `Depends()`

**Given** `models/dummy.py` defines the `Dummy` SQLModel class
**When** I inspect the model
**Then** it serves as both ORM mapping and Pydantic validation model (single class definition)
**And** `__tablename__` is explicitly set to `"DUMMY"` (UPPER_SNAKE_CASE)
**And** JSON serialization uses camelCase field names via Pydantic `alias_generator`

**Given** the database engine is created at startup
**When** the application initializes
**Then** `SQLModel.metadata.create_all` is called to ensure the `DUMMY` table exists

**Given** a `Dummy` instance is created with invalid data
**When** Pydantic validation runs
**Then** a validation error is raised before any database interaction occurs

## Story 1.5: REST API Endpoints and Service Layer

As a **software engineer**,
I want **working GET and POST endpoints for `/dummies` backed by a service layer, with full API documentation**,
So that **I can exercise a complete request-response cycle and use the `/dummies` resource as a copy-and-adapt template for new domain resources**.

**Acceptance Criteria:**

**Given** the application is running
**When** I send `GET /dummies`
**Then** the response status is 200
**And** the response body is a JSON array of all Dummy records from the database
**And** all JSON field names use camelCase

**Given** the application is running
**When** I send `POST /dummies` with a valid Dummy JSON payload (camelCase fields)
**Then** the response status is 201
**And** the response body is the created Dummy record with its assigned ID in camelCase JSON

**Given** the application is running
**When** I send `POST /dummies` with an invalid or malformed JSON payload
**Then** the response returns a structured error with the appropriate error code, message, and detail

**Given** `services/dummy_service.py` exists
**When** I inspect the code
**Then** business logic for listing and creating dummies is in the service layer — not in route handlers
**And** the service receives a database session via function parameters (passed from the route's `Depends()`)

**Given** the application is running
**When** I navigate to `/docs`
**Then** Swagger UI renders with the `/dummies` endpoints documented, including request/response schemas
**And** ReDoc is accessible at `/redoc`

**Given** the application startup sequence
**When** the app initializes
**Then** configuration validates first, then database engine is created, then middleware is registered, then routes are included — following the defined startup order

## Story 1.7: Health Check Endpoint

As a **software engineer**,
I want **a `GET /health` endpoint that confirms the Python runtime and FastAPI application are operational**,
So that **container orchestrators, load balancers, and the Docker Compose health check can determine whether the application process is alive and serving**.

**Acceptance Criteria:**

**Given** the application is running
**When** I send `GET /health`
**Then** the response status is 200
**And** the response body is a JSON object indicating the application is healthy (e.g., `{"status": "UP"}`)

**Given** the `/health` endpoint implementation
**When** I inspect the code
**Then** it uses standard FastAPI routing (a plain route on the app or a dedicated router) with no external health-check libraries

**Given** the `/health` endpoint
**When** I inspect the route registration
**Then** the endpoint is excluded from OpenAPI documentation (not a business API)
**And** it is excluded from Prometheus request metrics and OTEL trace instrumentation to avoid noise

## Story 1.6: Configurable Database Driver with SQLite Default

As a **software engineer**,
I want **the application to default to SQLite in-memory when no database driver is configured**,
So that **I can clone the project, run it immediately without standing up MariaDB, and still exercise the full request-response cycle**.

**Acceptance Criteria:**

**Given** `core/config.py` defines a `db_driver` setting
**When** `DB_DRIVER` is not set in the environment or `.env`
**Then** it defaults to `"sqlite"` and the application starts using an in-memory SQLite database

**Given** `DB_DRIVER=mysql+pymysql` is set
**When** the application starts
**Then** it connects to MariaDB using the `db_host`, `db_port`, `db_user`, `db_password`, and `db_name` settings

**Given** the application is running with the SQLite driver
**When** I send requests to `GET /dummies` and `POST /dummies`
**Then** the endpoints work correctly and data persists for the lifetime of the process

**Given** `core/database.py` creates the engine
**When** the driver is `sqlite`
**Then** `StaticPool` is used so all requests share the same in-memory database
**And** `check_same_thread=False` is set for SQLite compatibility

**Given** `.env.example` exists
**When** I inspect its contents
**Then** the `DB_DRIVER` options are documented with their meanings
