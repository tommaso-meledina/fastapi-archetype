# PROJECT_CONTEXT

This document is the authoritative reference for LLM agents contributing to fastapi-archetype. It describes every capability, pattern, convention, and constraint in the project. Agents must not introduce technologies, libraries, or patterns that are not documented here without explicit human approval.

## Identity

- **Name:** fastapi-archetype
- **Version:** 0.1.0
- **Python:** >=3.14
- **Purpose:** Production-grade FastAPI reference implementation. The domain (a `/dummies` CRUD resource) is intentionally trivial; the value is in the proven integration of enterprise cross-cutting concerns. Designed as a copy-and-adapt template for new microservices.

## Technology Stack

All dependencies are declared in `pyproject.toml`. Do not add or replace dependencies without human approval.

### Runtime

| Library | Version constraint | Role |
|---|---|---|
| fastapi | >=0.135.1 | Web framework |
| uvicorn | >=0.41.0 | ASGI server |
| sqlmodel | >=0.0.37 | ORM + Pydantic validation (single model definition) |
| pymysql | >=1.1.2 | MariaDB driver (pure Python) |
| pydantic-settings | >=2.13.1 | Typed configuration from env / .env |
| opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation-fastapi | >=1.39.1 / >=0.60b1 | Distributed tracing |
| prometheus-fastapi-instrumentator | >=7.1.0 | HTTP metrics auto-instrumentation |
| prometheus_client | (transitive) | Custom metrics |
| slowapi | >=0.1.9 | Per-endpoint rate limiting |
| PyJWT[crypto] | >=2.9.0 | JWT validation (Entra auth) |
| httpx | (transitive at runtime via auth) | Outbound HTTP for JWKS/token/Graph |

### Dev

| Library | Role |
|---|---|
| pytest >=8.0 | Test runner |
| pytest-cov >=6.0 | Coverage reporting |
| httpx >=0.28.1 | TestClient transport |
| ruff >=0.15.4 | Linting and formatting |

### Build and Tooling

| Tool | Role |
|---|---|
| uv | Dependency management, lock file, virtualenv, build backend (`uv_build`) |
| Docker (python:3.14-slim) | Multi-stage container image |
| Docker Compose | Full-stack dev environment (compose/ directory) |

## Project Structure

```
src/fastapi_archetype/
├── main.py                          # FastAPI app, lifespan, exception handlers, router registration, OTEL instrumentation
├── aop/
│   └── logging_decorator.py         # log_io decorator + apply_logging(module)
├── api/
│   ├── v1/
│   │   ├── __init__.py              # APIRouter(prefix="/v1"), includes resource routers
│   │   └── dummy_routes.py          # GET/POST /v1/dummies
│   └── v2/
│       ├── __init__.py              # APIRouter(prefix="/v2"), includes resource routers
│       └── dummy_routes.py          # GET/POST /v2/dummies (admin role on POST)
├── auth/
│   ├── contracts.py                 # AuthProvider, RoleMappingProvider ABCs; error types
│   ├── dependencies.py              # require_auth, require_role(Role), get_current_principal
│   ├── facade.py                    # AuthFacade (boundary around provider)
│   ├── factory.py                   # build_auth_facade(settings) -> AuthFacade
│   ├── models.py                    # Principal dataclass, Role StrEnum
│   └── providers/
│       ├── entra.py                 # EntraExternalAuthProvider (JWT, OAuth, Graph)
│       ├── none.py                  # NoAuthProvider (dev bypass, grants all roles)
│       └── role_mapping.py          # BasicRoleMappingProvider (identity mapping)
├── core/
│   ├── config.py                    # AppSettings(BaseSettings) — all env vars
│   ├── constants.py                 # ResourceDefinition dataclass, DUMMIES, HEALTH_PATH
│   ├── database.py                  # get_engine(settings), get_session() generator
│   ├── errors.py                    # ErrorCode enum, AppException, exception handlers
│   └── rate_limit.py               # Limiter instance (slowapi, keyed by remote address)
├── models/
│   └── dummy.py                     # Dummy(SQLModel, table=True) with camelCase aliases
├── observability/
│   ├── logging.py                   # configure_logging(settings), PlainFormatter, JsonFormatter, SpanFilter, secret redaction
│   ├── otel.py                      # setup_otel(app, settings) -> TracerProvider
│   └── prometheus.py                # Metrics dataclass, dummies_created_total counter, setup_prometheus(app)
└── services/
    ├── __init__.py                  # Imports all service modules and calls apply_logging() on each
    ├── v1/
    │   └── dummy_service.py         # get_all_dummies, create_dummy
    └── v2/
        └── dummy_service.py         # get_all_dummies, create_dummy (with INFO logging and v2 metric label)

tests/
├── conftest.py                      # SQLite in-memory engine, session, TestClient with DI override
├── aop/
│   └── test_logging_decorator.py
├── api/
│   ├── test_health.py
│   ├── test_dummy_routes.py         # v1 endpoints
│   └── test_v2_dummy_routes.py      # v2 endpoints
├── auth/
│   ├── conftest.py                  # RSA keypair, JWKS, JWT signing fixtures (synthetic IdP)
│   ├── test_dependencies.py
│   ├── test_external_provider.py
│   ├── test_facade.py
│   ├── test_entra_integration.py    # Full Entra flow with monkeypatched HTTP
│   └── test_role_mapping.py
├── core/
│   ├── test_config.py
│   ├── test_errors.py
│   └── test_rate_limit.py
├── observability/
│   ├── test_logging.py
│   └── test_prometheus.py
└── services/
    ├── v1/
    │   └── test_dummy_service.py
    └── v2/
        └── test_dummy_service.py

compose/
├── .env                             # Service-level env vars for Docker Compose
├── docker-compose.yaml              # mariadb, fastapi-archetype, grafana, jaeger, otel-collector, prometheus
└── observability/
    ├── otel-collector-config.yaml
    └── prometheus.yaml
```

## Capabilities and Implementation Details

### 1. REST API

Endpoints are defined in route modules under `api/v1/` and `api/v2/`. Each version has its own `APIRouter` with a prefix (`/v1`, `/v2`). Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at the root, unversioned.

Current endpoints:

| Method | Path | Auth | Rate limit setting |
|---|---|---|---|
| GET | `/health` | None | None |
| GET | `/metrics` | None | None |
| GET | `/docs` | None | None |
| GET | `/redoc` | None | None |
| GET | `/v1/dummies` | None | `rate_limit_get_dummies` |
| POST | `/v1/dummies` | `require_auth` | `rate_limit_post_dummies` |
| GET | `/v2/dummies` | None | `rate_limit_get_dummies` |
| POST | `/v2/dummies` | `require_role(Role.ADMIN)` | `rate_limit_post_dummies` |

All request/response payloads are JSON. Models use `alias_generator=_to_camel` and `populate_by_name=True` for camelCase serialization.

### 2. Data Persistence

- **ORM:** SQLModel — each model is defined once as `SQLModel, table=True`, serving both ORM and Pydantic validation.
- **Database driver:** Configurable via `DB_DRIVER`. Defaults to `sqlite` (in-memory with `StaticPool`). Production uses `mysql+pymysql` (MariaDB).
- **Session management:** `get_session()` is a generator yielding `Session` instances, injected into routes via `Depends(get_session)`. Tests override this dependency with a test-scoped SQLite session.
- **Schema management:** `SQLModel.metadata.create_all(engine)` in the lifespan. No migration tool (Alembic) is in scope.

### 3. Configuration Management

`core/config.py` defines `AppSettings(BaseSettings)` using pydantic-settings. All settings load from environment variables with `.env` file fallback. The application validates at startup and fails fast on invalid values.

Every configurable value is a field on `AppSettings`. New settings must be added as fields on this class. See `.env.example` for the complete reference.

### 4. Structured Error Handling

`core/errors.py` defines:

- `ErrorCode` enum — each member carries `(code, message, http_status)`. This is the single source of truth for all error codes.
- `AppException(error_code, detail)` — raised anywhere in the application.
- Three global exception handlers registered in `main.py`: `AppException`, `RateLimitExceeded`, `RequestValidationError`.

All error responses use the shape `{"errorCode": str, "message": str, "detail": any}`.

New error codes must be added to the `ErrorCode` enum. Raise `AppException(ErrorCode.XXX)` — never return raw `JSONResponse` for errors.

### 5. API Versioning

Versioning uses URL prefixes via `APIRouter(prefix="/v1")` and `APIRouter(prefix="/v2")`. Each version has its own routes module and service module. Version routers are included in `main.py`.

To add a new version: create `api/v3/`, `services/v3/`, register the router in `main.py`, and wire AOP logging in `services/__init__.py`.

### 6. AOP Function Logging

`aop/logging_decorator.py` provides:

- `log_io(func)` — decorator that logs inputs at DEBUG, return values at DEBUG, and exceptions at ERROR. Exception-path logging ensures failures surface in production logs without requiring DEBUG verbosity.
- `apply_logging(module)` — programmatically wraps all public functions defined in a module with `log_io` at import time. Only functions whose `__module__` matches the target are wrapped (re-exported imports are skipped). Individual service functions carry no decorator annotation.

`services/__init__.py` imports every service module and calls `apply_logging()` on each. New service modules must be added there.

### 7. OpenTelemetry Distributed Tracing

`observability/otel.py` configures a `TracerProvider` with an optional `OTLPSpanExporter` (gRPC). `FastAPIInstrumentor.instrument_app()` adds spans to all HTTP requests (the `/metrics` endpoint is excluded). The tracer provider is shut down in the lifespan exit.

Controlled by `OTEL_EXPORT_ENABLED` (default `false`) and `OTEL_EXPORTER_ENDPOINT`.

### 8. Prometheus Metrics

`observability/prometheus.py` provides:

- `Instrumentator().instrument(app).expose(app)` — auto-instruments HTTP request count, latency, and status at `/metrics`.
- `metrics.counters.dummies_created_total` — a custom `Counter` with `api_version` label, incremented in service functions after successful creation.

The `Metrics` and `Counters` dataclasses hold all custom metrics. New custom metrics must be added as fields on these dataclasses and instantiated at module level.

### 9. Rate Limiting

`core/rate_limit.py` creates a `Limiter` instance (slowapi) keyed by `get_remote_address`. Routes apply `@limiter.limit(settings.rate_limit_xxx)`. The limiter is attached to `app.state.limiter` in `main.py`. A custom exception handler converts `RateLimitExceeded` into the standard error response format.

Rate limit values are strings like `"100/minute"` or `"10/minute"`, configurable via `AppSettings` fields.

### 10. Authentication and Authorization

Architecture: `AuthProvider` (ABC) → concrete providers (`NoAuthProvider`, `EntraExternalAuthProvider`) → `AuthFacade` (boundary) → FastAPI dependencies (`require_auth`, `require_role`).

**Auth modes** (controlled by `AUTH_TYPE`):

- `none`: `NoAuthProvider` returns a synthetic principal with all roles. No token validation.
- `entra`: `EntraExternalAuthProvider` validates bearer JWT (signature via JWKS, standard claims, issuer, optional audience), maps claims to `Principal`, supports client_credentials and OBO token acquisition, and optional Graph-based role enrichment.

**Role model:** `Role` is a `StrEnum` with members `ADMIN`, `WRITER`, `READER`. `RoleMappingProvider.to_external(role_name)` maps internal labels to external identifiers. `BasicRoleMappingProvider` is an identity mapping.

**Dependencies:**

- `require_auth` — ensures a valid `Principal` exists (any authenticated user).
- `require_role(Role.XXX)` — returns a dependency that additionally checks the principal has the required role.

**Error sanitization:** Auth failures raise `AppException(ErrorCode.UNAUTHORIZED)` or `AppException(ErrorCode.FORBIDDEN)`. Provider-specific details are logged server-side only, never exposed to clients.

**Factory:** `build_auth_facade(settings)` in `auth/factory.py` selects the provider based on `AUTH_TYPE`.

### 11. Containerization

**Dockerfile:** Multi-stage. Builder uses `uv` (copied from `ghcr.io/astral-sh/uv:0.10.7`) to resolve and install locked dependencies. Runtime uses `python:3.14-slim` with a non-root `app` user. No dev dependencies in the final image.

**Docker Compose** (`compose/docker-compose.yaml`):

| Service | Image | Port(s) |
|---|---|---|
| mariadb | mariadb:11 | 3306 |
| fastapi-archetype | Built from project root | 8000 |
| grafana | grafana/grafana-oss | 3001 |
| jaeger-all-in-one | jaegertracing/all-in-one | 16686 |
| otel-collector | otel/opentelemetry-collector-contrib | 4317, 4318 |
| prometheus | prom/prometheus | 9090 |

### 12. Testing

- **Framework:** pytest with `testpaths=["tests"]` and `pythonpath=["src"]`.
- **Database:** SQLite in-memory with `StaticPool`. Tests override `get_session` via `app.dependency_overrides`.
- **Auth in tests:** `AUTH_TYPE=none` is set via `os.environ.setdefault` in `tests/conftest.py`. Auth integration tests in `tests/auth/` use a synthetic IdP: test-generated RSA keypair, JWKS fixture, JWT signing helper, monkeypatched HTTP calls.
- **Rate limiting:** `limiter.reset()` is called in the client fixture to prevent cross-test pollution.
- **Coverage target:** >90%.
- **Test organization mirrors source:** `tests/api/`, `tests/auth/`, `tests/core/`, `tests/services/`, `tests/aop/`, `tests/observability/`.

### 13. Code Quality

Ruff is configured in `pyproject.toml`:

- `target-version = "py314"`
- `line-length = 88`
- Lint rules: `E`, `W`, `F`, `I`, `N`, `UP`, `B`, `SIM`, `TCH`
- `extend-immutable-calls = ["fastapi.Depends", "Depends"]`
- `known-first-party = ["fastapi_archetype"]`

## Conventions and Patterns

### Module organization

- One model per file in `models/`.
- One resource's routes per file in `api/v{n}/`.
- One resource's service per file in `services/v{n}/`.
- The version router `__init__.py` aggregates resource routers.
- `services/__init__.py` aggregates AOP logging application.

### Constants

- All resource paths, names, and descriptions are `ResourceDefinition` instances in `core/constants.py`.
- `HEALTH_PATH` is a plain string constant.
- No string literals for paths or resource names in route/service code.

### Configuration

- Every configurable value is a typed field on `AppSettings`.
- Environment variable names match field names in UPPER_CASE.
- Defaults are provided for all fields except auth-specific fields required when `AUTH_TYPE=entra`.

### Error handling

- All error codes live in the `ErrorCode` enum.
- Application code raises `AppException(ErrorCode.XXX, detail=...)`.
- Auth code raises `AuthError` subclasses internally; `dependencies.py` catches and translates them to `AppException`.
- Never return raw `JSONResponse` for error cases.

### Dependency injection

- Database sessions: `Depends(get_session)`.
- Auth: `Depends(require_auth)` or `Depends(require_role(Role.XXX))`.
- Rate limiting: `@limiter.limit(settings.rate_limit_xxx)` decorator.
- All DI-based dependencies are overridable in tests via `app.dependency_overrides`.

### Testing

- Every new route needs endpoint tests in `tests/api/`.
- Every new service needs unit tests in `tests/services/`.
- Use the existing `client` and `session` fixtures from `tests/conftest.py`.
- Auth-related tests go in `tests/auth/` and use the synthetic IdP fixtures from `tests/auth/conftest.py`.

### Code style

- `from __future__ import annotations` at the top of every module.
- Type-checking-only imports guarded by `if TYPE_CHECKING:`.
- No code comments except where they explain non-obvious intent.
- No dead code or placeholder implementations.
- camelCase API responses via Pydantic `alias_generator`.

### Logging

- `configure_logging(settings)` in `observability/logging.py` is called once in the lifespan via `logging.config.dictConfig`.
- `LOG_MODE` (`plain`/`json`, default `plain`) selects the active formatter; invalid values fall back to `plain` with a startup warning.
- Plain format: UTC ISO-8601 timestamp, `[traceId]`, `[spanId]`, level, logger name, message. Exception rendering shows type and message only.
- JSON format: one NDJSON object per line with camelCase fields (`timestamp`, `level`, `logger`, `message`, `traceId`, `spanId`). Exceptions add `exceptionType`, `exceptionMessage`, `stackTrace`.
- `SpanFilter` injects `traceId` and `spanId` from the current OpenTelemetry span context; `NO_TRACE_ID`/`NO_SPAN_ID` when no trace is active.
- Baseline secret redaction masks obvious sensitive values (passwords, tokens, API keys, authorization headers) in both modes.
- Modules obtain loggers via `logging.getLogger(__name__)`.
- AOP logging is at DEBUG level for I/O and ERROR level for exceptions (with `exc_info=True`); application-level logging in services uses INFO.

## Anti-Patterns to Avoid

- Do not add global middleware for auth — use explicit `Depends()` per route.
- Do not scatter string literals for paths or error codes — use `core/constants.py` and `ErrorCode`.
- Do not create new settings outside `AppSettings` — add fields there.
- Do not add Alembic or database migration tooling — schema is managed via `create_all`.
- Do not add a local token-issuance endpoint — auth is external IdP only.
- Do not add libraries not listed in the technology stack without human approval.
- Do not add code comments that merely narrate what the code does.
- Do not skip `from __future__ import annotations` in new modules.
- Do not modify `tests/conftest.py` fixtures to be resource-specific — they are generic by design.

## Adding a New Resource

To add a new resource (e.g., `Widget`):

1. **Model:** Create `models/widget.py` with `class Widget(SQLModel, table=True)`, camelCase alias config, and `__tablename__`.
2. **Constant:** Add `WIDGETS = ResourceDefinition(...)` to `core/constants.py`.
3. **Service:** Create `services/v1/widget_service.py` with query/mutation functions taking `Session` as first argument.
4. **AOP:** Import and `apply_logging()` the service module in `services/__init__.py`.
5. **Routes:** Create `api/v1/widget_routes.py` with `APIRouter(prefix=WIDGETS.path, tags=[WIDGETS.name])`, rate-limited endpoints, auth dependencies as needed.
6. **Router registration:** Include the widget router in `api/v1/__init__.py`.
7. **Tests:** Add `tests/api/test_widget_routes.py` and `tests/services/v1/test_widget_service.py` using existing fixtures.
8. **Custom metrics (if needed):** Add counters to the `Counters` dataclass in `observability/prometheus.py`.
9. **Rate limits (if needed):** Add `rate_limit_get_widgets` / `rate_limit_post_widgets` fields to `AppSettings` and corresponding entries to `.env.example`.

The new resource automatically inherits OpenTelemetry tracing, Prometheus HTTP metrics, structured error handling, and the configured auth mode.
