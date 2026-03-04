# fastapi-archetype

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![AI Assisted](https://img.shields.io/badge/AI-Assisted_Code-blueviolet)](https://cursor.com)

## Summary

- [Purpose](#purpose)
- [Usage](#usage)
- [Capabilities](#capabilities)

## Purpose

A production-grade Python 3.14 / FastAPI reference implementation that integrates enterprise capabilities into a single, cohesive application. The domain is intentionally trivial (a `/dummies` CRUD resource) so the infrastructure and cross-cutting concerns remain the focus.

The project demonstrates the following capabilities working together end-to-end:

- REST API with CRUD operations and automatic OpenAPI documentation
- SQLModel ORM with configurable database driver (SQLite in-memory or MariaDB)
- Typed configuration management via pydantic-settings with `.env` support
- Enum-based structured error handling with consistent JSON responses
- URL-prefix API versioning (`/v1`, `/v2`) with `APIRouter`
- Decorator-based AOP function I/O logging applied at the package level
- OpenTelemetry distributed tracing with optional OTLP export
- Prometheus metrics (auto-instrumented HTTP metrics and custom business counters)
- Per-endpoint rate limiting with environment-configurable thresholds
- External IdP bearer-token authentication and role-based access control
- Multi-stage Docker image and a Docker Compose stack with MariaDB, Jaeger, OTEL Collector, Prometheus, and Grafana
- pytest suite with >90% coverage using SQLite in-memory and synthetic IdP fixtures
- Ruff linting and formatting targeting Python 3.14

Clone or scaffold from this project to get all of the above working on first run.

## Usage

### Using `uv`

Install dependencies:

```bash
uv sync
```

Run the application (uses SQLite in-memory by default — no database setup needed):

```bash
uv run uvicorn fastapi_archetype.main:app --reload
```

To use MariaDB instead, set `DB_DRIVER=mysql+pymysql` in a `.env` file (see `.env.example`).

### Using Docker

Build the image:

```bash
docker build -t fastapi-archetype .
```

Run the container (uses SQLite in-memory by default — no `.env` file required):

```bash
docker run -p 8000:8000 fastapi-archetype
```

To pass custom configuration, use `--env-file`:

```bash
docker run --env-file .env -p 8000:8000 fastapi-archetype
```

### Using Docker Compose

The `compose/` directory contains a full production-like environment. From the project root:

```bash
docker compose -f compose/docker-compose.yaml up --build
```

This starts the application against MariaDB with the full observability stack (OTEL Collector, Jaeger, Prometheus, Grafana). See [Docker Compose Observability Stack](#docker-compose-observability-stack) for service details and URLs.

## Capabilities

### REST API with CRUD Operations

The application exposes a minimal `Dummy` resource through versioned endpoints. All payloads use JSON with camelCase field names (via Pydantic alias generation).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/dummies` | List all dummies |
| POST | `/v1/dummies` | Create a dummy (requires authentication) |
| GET | `/v2/dummies` | List all dummies |
| POST | `/v2/dummies` | Create a dummy (requires admin role) |
| GET | `/health` | Health check |

**Try it:** start the application and send requests with `curl`:

```bash
curl http://localhost:8000/v1/dummies
curl -X POST http://localhost:8000/v1/dummies \
  -H "Content-Type: application/json" \
  -d '{"name": "example", "description": "a test dummy"}'
```

### Data Persistence with SQLModel

The `Dummy` model is defined once using SQLModel, serving as both the ORM mapping (to the `DUMMY` table) and the Pydantic validation schema. Database sessions are injected via FastAPI's `Depends()` pattern, making the database backend swappable without touching application logic.

By default the application starts with SQLite in-memory — no external database needed. Set `DB_DRIVER=mysql+pymysql` and the corresponding `DB_*` variables to connect to MariaDB.

**Try it:** run the application, create a few dummies via POST, then verify they persist with GET. Restart with the default SQLite driver to confirm the in-memory database starts fresh.

### Configuration Management

All settings are loaded from environment variables (with `.env` file support) using pydantic-settings. The application validates configuration at startup and fails fast if required values are missing or malformed. See `.env.example` for the full list of supported variables.

**Try it:** set `LOG_LEVEL=DEBUG` in a `.env` file and restart the application to see detailed AOP and framework logs on stdout.

### Structured Error Handling

All error responses follow a consistent JSON structure with `errorCode`, `message`, and `detail` fields. Error codes are defined in a central enum (`ErrorCode`) that maps each code to its HTTP status and message. Custom exception handlers cover application errors, validation failures, and rate-limit violations.

**Try it:** send an invalid POST body to trigger a validation error:

```bash
curl -X POST http://localhost:8000/v1/dummies \
  -H "Content-Type: application/json" \
  -d '{}'
```

### API Documentation

FastAPI auto-generates an OpenAPI 3.x specification from route and model definitions. Interactive documentation is available at two endpoints.

**Try it:** open your browser and navigate to:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

### API Versioning

Business endpoints are organized under versioned URL prefixes (`/v1/`, `/v2/`) using FastAPI's `APIRouter`. Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at the root, unversioned. This demonstrates how to evolve an API while keeping infrastructure routes stable.

The v2 router enforces stricter authorization (admin role required for POST) to illustrate how versioning and access control compose together.

**Try it:** compare the behavior of `POST /v1/dummies` (requires any authenticated principal) versus `POST /v2/dummies` (requires admin role).

### AOP Function Logging

A `log_io` decorator logs function input arguments and return values at DEBUG level. The `apply_logging` function wraps all public functions in a module automatically — no per-function modification needed. The services layer uses this to provide full call tracing.

**Try it:** set `LOG_LEVEL=DEBUG` and call any endpoint. Observe the `invoked with args (...)` and `returned ...` log lines on stdout for every service function.

### OpenTelemetry Distributed Tracing

The application instruments all incoming HTTP requests with OpenTelemetry spans. When `OTEL_EXPORT_ENABLED=true`, traces are exported to an OTLP collector via gRPC. The tracer provider shuts down cleanly on application exit.

**Try it:** start the Docker Compose stack, send a few requests, then open Jaeger at <http://localhost:16686> and search for traces from `fastapi-archetype`.

### Prometheus Metrics

The application exposes auto-instrumented HTTP metrics (request count, latency, status codes) and a custom business counter (`dummies_created_total`, labeled by `api_version`) at the `/metrics` endpoint.

**Try it:** send a few requests and inspect the metrics:

```bash
curl http://localhost:8000/metrics | grep dummies_created_total
```

With the Docker Compose stack running, open Prometheus at <http://localhost:9090> and query `dummies_created_total` or `http_request_duration_seconds_bucket`.

### Rate Limiting

Per-endpoint rate limits are enforced using `slowapi`, keyed by client IP. Default thresholds are 100 requests/minute for GET and 10 requests/minute for POST, configurable via `RATE_LIMIT_GET_DUMMIES` and `RATE_LIMIT_POST_DUMMIES` environment variables. Exceeding the limit returns a 429 response with standard rate-limit headers and a structured error body.

**Try it:** lower the POST limit and trigger a 429:

```bash
RATE_LIMIT_POST_DUMMIES=2/minute uv run uvicorn fastapi_archetype.main:app &
for i in 1 2 3; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/v1/dummies \
    -H "Content-Type: application/json" -d '{"name": "test"}'
done
```

### Authentication and Role-Based Access Control

The auth subsystem supports two modes controlled by `AUTH_TYPE`:

- **`none`** (default): bypasses authentication for local development.
- **`entra`**: validates external IdP bearer tokens (JWT signature and claim verification via remote JWKS), maps claims into a typed `Principal` model, and enforces role-based access through `require_auth` and `require_role` FastAPI dependencies.

The architecture includes a pluggable `RoleMappingProvider` contract for bridging internal role labels to external identity systems, outbound OAuth token acquisition (client credentials and on-behalf-of flows), and sanitized error responses that log provider-specific details server-side only.

**Try it:** run with `AUTH_TYPE=none` (default) and observe that write endpoints accept requests without tokens. Review `tests/auth/` for integration tests that use a synthetic IdP (test-generated RSA keypair with monkeypatched HTTP) to verify the full Entra flow.

### Production-Ready Containerization

The multi-stage Dockerfile uses `python:3.14-slim` as the runtime base and `uv` for dependency resolution in the builder stage. The final image runs as a non-root `app` user with no build tools or dev dependencies.

**Try it:** build and run the image:

```bash
docker build -t fastapi-archetype .
docker run -p 8000:8000 fastapi-archetype
```

### Docker Compose Observability Stack

The `compose/` directory provides a full production-like environment with the following services:

| Service | Port | Purpose |
|---------|------|---------|
| fastapi-archetype | 8000 | Application (connected to MariaDB) |
| MariaDB | 3306 | Persistent database |
| OTEL Collector | 4317, 4318 | Receives OTLP traces, exports to Jaeger and Prometheus |
| Jaeger | 16686 | Distributed trace visualization |
| Prometheus | 9090 | Metrics scraping and querying |
| Grafana | 3001 | Dashboards and visualization |

**Try it:** start the stack, then open each UI:

```bash
docker compose -f compose/docker-compose.yaml up --build
```

- Application: <http://localhost:8000/docs>
- Jaeger: <http://localhost:16686>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3001>

### Testing

The test suite uses pytest with SQLite in-memory for integration tests — no external infrastructure needed. Tests are organized by layer (`api/`, `auth/`, `core/`, `services/`, `aop/`, `observability/`). Auth integration tests use a synthetic IdP with test-generated RSA keypairs and monkeypatched HTTP calls. The suite targets >90% code coverage.

**Try it:** run the full suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=fastapi_archetype --cov-report=term-missing
```

### Code Quality

Ruff enforces linting and formatting rules targeting Python 3.14, including pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, and flake8-simplify checks.

**Try it:** check the codebase:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```
