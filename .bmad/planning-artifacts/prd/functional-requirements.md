# Functional Requirements

## REST API

- FR1: The application exposes a GET endpoint that returns all Dummy records from the database
- FR2: The application exposes a POST endpoint that accepts a Dummy object, validates it, and creates a record in the database
- FR3: The application returns structured error responses with unique error codes and messages for all failure scenarios
- FR4: The application serves all request and response payloads in JSON format
- FR29: The application exposes a `GET /health` endpoint that returns the application's health status, confirming the Python runtime and FastAPI framework are operational

## Data Persistence

- FR5: The application connects to a MariaDB database for persistent storage
- FR5a: The application supports a configurable database driver (`DB_DRIVER`) that defaults to SQLite in-memory, allowing the application to start and serve requests without external database infrastructure
- FR6: The application maps a Dummy model to a DUMMY table using SQLModel, with a single model definition serving both ORM and API validation
- FR7: The application validates all input data against the Dummy model schema before persisting

## Configuration Management

- FR8: The application loads configuration values from a `.env` file at startup
- FR9: The application validates that all required configuration values are present and well-formed at startup, failing fast if not

## API Documentation

- FR10: The application automatically generates an OpenAPI 3.x specification from its route and model definitions
- FR11: The application serves an interactive Swagger UI at `/docs`
- FR12: The application serves a ReDoc interface at `/redoc`

## Testing

- FR13: The application's unit tests mock all external dependencies (database, OTEL collector, etc.) and test components in isolation
- FR14: The application's integration tests run against an in-memory SQLite database, requiring no external infrastructure
- FR15: The application's test suite covers all endpoints with both valid and invalid input scenarios
- FR16: The application's test suite achieves >90% code coverage; code that is particularly difficult to test (e.g., strictly non-functional components) may be excluded from coverage measurement through standard exclusion mechanisms

## Cross-Cutting Concerns (AOP)

- FR17: The application provides a decorator-based AOP mechanism that logs function input arguments and return values
- FR17a: The application configures the Python logging subsystem at startup, directing all log output to stdout with a configurable log level (defaulting to INFO)
- FR18: The AOP logging decorator can be applied to all functions within a designated package without modifying each function individually
- FR19: The AOP logging mechanism uses plain Python decorators, falling back to `wrapt` only if plain decorators prove insufficient

## Observability

- FR20: The application emits OpenTelemetry traces for incoming requests
- FR21: The application exports traces to an OTEL collector when one is configured
- FR22: The application exposes Prometheus metrics at a `/metrics` endpoint
- FR23: The application automatically instruments HTTP request metrics (count, latency, status) for Prometheus scraping
- FR23a: The application demonstrates a custom Prometheus metric (e.g., a business counter) alongside the auto-instrumented HTTP metrics, serving as a replicable pattern for adding application-specific metrics

## Containerization

- FR24: The application provides a Dockerfile that builds a production-ready container image
- FR25: The Docker image starts the application and serves requests without additional configuration beyond the `.env` file

## API Versioning

- FR37: The application organizes all business API endpoints under a versioned URL prefix (e.g., `/v1/dummies`) using FastAPI's `APIRouter`
- FR38: Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at the root level, unversioned

## Rate Limiting

- FR30: The application enforces per-endpoint rate limits on API requests using `slowapi`
- FR31: Rate limit thresholds are configurable via environment variables, with sensible defaults
- FR32: The application returns a 429 response with standard rate-limit headers and a structured error body when limits are exceeded

## Authentication & Authorization

- FR33: The application supports JWT-based authentication using FastAPI's built-in OAuth2 utilities
- FR34: The application provides a token endpoint for obtaining JWT access tokens
- FR35: The application supports role-based access control (RBAC), allowing selective endpoint protection via FastAPI's dependency injection
- FR36: Authentication configuration (JWT secret, algorithm, token expiry) is configurable via environment variables

## Code Organization

- FR26: All resource paths, configuration keys, and shared constants are defined in centralized constant files, not scattered as string literals
- FR27: All error codes and their associated messages are defined in a single central location
- FR28: Resource definitions MAY be organized as structured objects grouping related constants (path, name, description) per REST resource
