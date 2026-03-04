# Requirements Inventory

## Functional Requirements

FR1: The application exposes a GET endpoint that returns all Dummy records from the database
FR2: The application exposes a POST endpoint that accepts a Dummy object, validates it, and creates a record in the database
FR3: The application returns structured error responses with unique error codes and messages for all failure scenarios
FR4: The application serves all request and response payloads in JSON format
FR29: The application exposes a `GET /health` endpoint that returns the application's health status, confirming the Python runtime and FastAPI framework are operational
FR5: The application connects to a MariaDB database for persistent storage
FR6: The application maps a Dummy model to a DUMMY table using SQLModel, with a single model definition serving both ORM and API validation
FR7: The application validates all input data against the Dummy model schema before persisting
FR8: The application loads configuration values from a `.env` file at startup
FR9: The application validates that all required configuration values are present and well-formed at startup, failing fast if not
FR10: The application automatically generates an OpenAPI 3.x specification from its route and model definitions
FR11: The application serves an interactive Swagger UI at `/docs`
FR12: The application serves a ReDoc interface at `/redoc`
FR13: The application's unit tests mock all external dependencies (database, OTEL collector, etc.) and test components in isolation
FR14: The application's integration tests run against an in-memory SQLite database, requiring no external infrastructure
FR15: The application's test suite covers all endpoints with both valid and invalid input scenarios
FR16: The application's test suite achieves >90% code coverage; code that is particularly difficult to test (e.g., strictly non-functional components) may be excluded from coverage measurement through standard exclusion mechanisms
FR17: The application provides a decorator-based AOP mechanism that logs function input arguments and return values
FR17a: The application configures the Python logging subsystem at startup, directing all log output to stdout with a configurable log level (defaulting to INFO)
FR18: The AOP logging decorator can be applied to all functions within a designated package without modifying each function individually
FR19: The AOP logging mechanism uses plain Python decorators, falling back to `wrapt` only if plain decorators prove insufficient
FR20: The application emits OpenTelemetry traces for incoming requests
FR21: The application exports traces to an OTEL collector when one is configured
FR22: The application exposes Prometheus metrics at a `/metrics` endpoint
FR23: The application automatically instruments HTTP request metrics (count, latency, status) for Prometheus scraping
FR24: The application provides a Dockerfile that builds a production-ready container image
FR25: The Docker image starts the application and serves requests without additional configuration beyond the `.env` file
FR26: All resource paths, configuration keys, and shared constants are defined in centralized constant files, not scattered as string literals
FR27: All error codes and their associated messages are defined in a single central location
FR28: Resource definitions MAY be organized as structured objects grouping related constants (path, name, description) per REST resource

## NonFunctional Requirements

NFR1: The codebase follows a consistent code style enforced by linting tools (e.g., ruff, flake8, or similar)
NFR2: The project structure is logically organized so that a developer unfamiliar with the codebase can locate any capability (model, route, test, AOP, config) within minutes
NFR3: Each capability area (ORM, AOP, observability, configuration, etc.) is cleanly separated so it can be understood, modified, or replaced independently
NFR4: The codebase contains no dead code, commented-out blocks, or placeholder implementations
NFR5: Code comments are avoided altogether; comments are only permitted where they explain non-obvious intent or constraints that the code itself cannot convey
NFR6: The Docker image runs consistently across Linux and macOS environments without modification
NFR7: The application has no host-specific dependencies beyond what is declared in `pyproject.toml` and the `.env` file
NFR8: A developer can understand the project structure and the role of each module by reading the project's documentation and code organization alone
NFR9: The patterns used for the `/dummies` resource (model, route, validation, tests, AOP, constants) are clear enough to serve as a copy-and-adapt template for new resources
NFR10: All configuration values have sensible defaults or clear documentation of required values, so a developer can get the application running with minimal setup

## Additional Requirements

**From Architecture — Starter Template:**
- Project initialization via `uv init fastapi-archetype` (clean init, no third-party template)
- Python 3.14 pinned via `pyproject.toml` `requires-python` and `uv python pin`
- `pyproject.toml` as single project configuration file
- `uv.lock` for reproducible dependency resolution

**From Architecture — Technology Decisions:**
- MariaDB driver: PyMySQL 1.1.2 (pure Python, zero system dependencies)
- ORM: SQLModel 0.0.37
- Configuration: pydantic-settings `BaseSettings` 2.13.1
- ASGI server: Uvicorn standalone 0.41.0
- Linting & formatting: Ruff 0.15.4
- Schema management: SQLModel `create_all` (no Alembic migrations in MVP)
- Session management: FastAPI `Depends()` with generator pattern for dual-database abstraction
- Error handling: Enum-based `ErrorCode` registry + custom `AppException` + global exception handler

**From Architecture — Project Structure:**
- `src/` layout per Python Packaging User Guide (`src/fastapi_archetype/`)
- Layered package structure: `api/`, `models/`, `core/`, `services/`, `aop/`, `observability/`
- `core/config.py` for pydantic-settings configuration
- `core/constants.py` for centralized constants and resource definitions
- `core/errors.py` for error code enum, AppException, and exception handler
- `core/database.py` for engine creation and session generator
- `tests/` at project root mirroring source structure

**From Architecture — Implementation Patterns:**
- camelCase JSON field names via Pydantic `alias_generator`
- UPPER_SNAKE_CASE table names with explicit `__tablename__`
- Direct SQLModel/Pydantic serialization for success responses (no envelope wrapper)
- Structured error response format: `errorCode`, `message`, `detail`
- Startup sequence: Config validation → DB engine → Middleware registration → Route inclusion
- `logging.getLogger(__name__)` per module; structured JSON in production, human-readable in dev
- AOP: Module-level `apply_logging(module)` targeting `services/` package
- Validation at API boundary only (Pydantic/SQLModel on request entry)
- Multi-stage Dockerfile with `python:3.14-slim` runtime base

**From Architecture — Containerization:**
- Multi-stage Dockerfile: build stage installs dependencies, runtime stage copies only what's needed
- `python:3.14-slim` as runtime base image (avoids Alpine musl issues)
- `.env` file as only external configuration input

## FR Coverage Map

| FR | Epic | Description |
|---|---|---|
| FR1 | Epic 1 | GET /dummies endpoint |
| FR2 | Epic 1 | POST /dummies endpoint |
| FR3 | Epic 1 | Structured error responses |
| FR4 | Epic 1 | JSON request/response format |
| FR5 | Epic 1 | MariaDB connection |
| FR6 | Epic 1 | Dummy SQLModel (ORM + validation) |
| FR7 | Epic 1 | Input validation against schema |
| FR8 | Epic 1 | .env config loading |
| FR9 | Epic 1 | Config validation / fail-fast |
| FR10 | Epic 1 | OpenAPI 3.x generation |
| FR11 | Epic 1 | Swagger UI at /docs |
| FR12 | Epic 1 | ReDoc at /redoc |
| FR13 | Epic 4 | Unit tests with mocked deps |
| FR14 | Epic 4 | Integration tests with SQLite |
| FR15 | Epic 4 | Full endpoint test coverage |
| FR16 | Epic 4 | >90% code coverage |
| FR17 | Epic 2 | Decorator-based AOP logging |
| FR17a | Epic 2 | Logging subsystem configuration (stdout, configurable level) |
| FR18 | Epic 2 | Package-level decorator application |
| FR19 | Epic 2 | Plain Python decorators (wrapt fallback) |
| FR20 | Epic 3 | OTEL traces for requests |
| FR21 | Epic 3 | Trace export to OTEL collector |
| FR22 | Epic 3 | Prometheus metrics at /metrics |
| FR23 | Epic 3 | HTTP request metrics instrumentation |
| FR24 | Epic 5 | Dockerfile for production image |
| FR25 | Epic 5 | Docker image runs with .env only |
| FR26 | Epic 1 | Centralized constants |
| FR27 | Epic 1 | Centralized error codes/messages |
| FR28 | Epic 1 | Optional structured resource objects |
| FR29 | Epic 1 | Health endpoint (runtime liveness) |
