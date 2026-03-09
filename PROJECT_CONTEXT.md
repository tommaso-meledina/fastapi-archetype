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
| sqlmodel | >=0.0.37 | ORM for entities; Pydantic for DTOs (see Data Persistence) |
| pymysql | >=1.1.2 | MariaDB driver (pure Python) |
| pydantic-settings | >=2.13.1 | Typed configuration from env / .env |
| opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation-fastapi | >=1.39.1 / >=0.60b1 | Distributed tracing |
| prometheus-fastapi-instrumentator | >=7.1.0 | HTTP metrics auto-instrumentation |
| prometheus_client | (transitive) | Custom metrics |
| slowapi | >=0.1.9 | Per-endpoint rate limiting |
| PyJWT[crypto] | >=2.9.0 | JWT validation (Entra auth) |
| httpx | (transitive at runtime via auth) | Outbound HTTP for JWKS/token endpoints |

### Dev

| Library | Role |
|---|---|
| pytest >=8.0 | Test runner |
| pytest-cov >=6.0 | Coverage reporting |
| httpx >=0.28.1 | TestClient transport |
| ruff >=0.15.4 | Linting and formatting |
| ty (version per lock file) | Type checking |

### Build and Tooling

| Tool | Role |
|---|---|
| uv | Dependency management, lock file, virtualenv, build backend (`uv_build`) |
| Docker (python:3.14-slim) | Multi-stage container image |
| Docker Compose | Local testing only (compose/ directory); not part of the product. |

## Project Structure

```
src/fastapi_archetype/
├── main.py                          # FastAPI app, lifespan, exception handlers, router registration, OTEL instrumentation
├── aop/
│   └── logging_decorator.py         # log_io decorator + apply_logging(module)
├── api/
│   ├── v1/
│   │   ├── __init__.py              # APIRouter(prefix="/v1"), includes resource routers
│   │   └── dummy_routes.py          # GET/POST/PUT /v1/dummies
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
│       ├── entra.py                 # EntraExternalAuthProvider (JWT, OAuth token acquisition)
│       ├── none.py                  # NoAuthProvider (dev bypass, grants all roles)
│       └── role_mapping.py          # BasicRoleMappingProvider (identity mapping)
├── core/
│   ├── config.py                    # AppSettings(BaseSettings) — all env vars
│   ├── constants.py                 # ResourceDefinition dataclass, DUMMIES, HEALTH_PATH
│   ├── database.py                  # get_engine(settings), get_session() generator
│   ├── errors.py                    # ErrorCode enum, AppException, exception handlers
│   └── rate_limit.py               # Limiter instance (slowapi, keyed by remote address)
├── models/
│   ├── entities/                    # ORM-only: one file per entity (SQLModel, table=True)
│   │   └── dummy.py                 # Dummy entity
│   └── dto/                         # API request/response only; versioned by API version
│       └── v1/
│           └── dummy.py             # PostDummiesRequest, GetDummiesResponse, PostDummiesResponse, PutDummiesRequest (Pydantic, camelCase)
├── factories/                       # Entity ↔ DTO mapping (Pydantic-only: model_validate, model_dump)
│   └── dummy.py                    # entity_to_get_response, entity_to_post_response, post_dto_to_entity, put_dto_to_entity
├── observability/
│   ├── logging.py                   # configure_logging(settings), PlainFormatter, JsonFormatter, SpanFilter, secret redaction
│   ├── otel.py                      # setup_otel(app, settings) -> TracerProvider
│   └── prometheus.py                # Metrics dataclass, dummies_created_total counter, setup_prometheus(app)
└── services/
    ├── __init__.py                  # Imports all service modules and calls apply_logging() on each
    ├── contracts/                   # Service contracts (ABCs or Protocol) — one module per logical service
    │   └── dummy_service.py         # DummyServiceV1Contract, DummyServiceV2Contract
    ├── factory.py                   # build_*_service(settings) — select implementation by settings.profile
    ├── v1/
    │   ├── implementations/         # Default and mock implementations for v1
    │   │   ├── default_dummy_service.py
    │   │   └── mock_dummy_service.py
    │   └── dummy_service.py        # Re-export or thin wrapper; routes depend on contract via DI
    └── v2/
        ├── implementations/
        │   ├── default_dummy_service.py
        │   └── mock_dummy_service.py
        └── dummy_service.py

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
├── docker-compose.yaml              # Local testing only: mariadb, fastapi-archetype, grafana, jaeger, otel-collector, prometheus
├── mariadb/
│   └── init/                        # MariaDB native init (runs on first start only)
│       └── schema.sql               # DUMMY and other app tables; DB name must match .env DATABASE_NAME
└── observability/
    ├── otel-collector-config.yaml
    └── prometheus.yaml

scripts/
├── remove_demo.py                   # Strip Dummy CRUD demo boilerplate
└── build_template.py                # Generate Cookiecutter template from reference implementation
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
| PUT | `/v1/dummies/{uuid}` | None | `rate_limit_get_dummies` |
| GET | `/v2/dummies` | None | `rate_limit_get_dummies` |
| POST | `/v2/dummies` | `require_role(Role.ADMIN)` | `rate_limit_post_dummies` |

All request/response payloads are JSON. Models use `alias_generator=_to_camel` and `populate_by_name=True` for camelCase serialization.

### 2. Data Persistence

- **Entities:** SQLModel classes with `table=True` live in `models/entities/` (one file per entity). They are used only for persistence and service-layer logic; they are not used as FastAPI request/response models.
- **DTOs:** Plain Pydantic models (no `table=True`) live in `models/dto/<version>/` (e.g. `v1/`). They define API request/response shapes with camelCase via `alias_generator` and are used only at the route boundary.
- **Factories:** The `factories/` package (one module per entity) provides entity ↔ DTO conversion using only Pydantic: `model_validate()` and `model_dump()`. No separate mapping library. Routes call factory functions at the boundary; services accept and return entities only.
- **Client identity (UUID vs ID):** Entities that need a stable, client-facing identifier have a `uuid` property (string, UUID format). Response DTOs expose `uuid` and **never** expose the internal persistence `id`. This keeps persistence details hidden and gives clients a stable reference for updates and links.
- **Update-by-UUID pattern (PUT):** For `PUT /v1/<resource>/{uuid}` with a body that includes `uuid` and updatable fields, follow this split so the route stays thin and the service owns resolution (IMPORTANT: this applies to mutations targeting entities-with-id in general, not just PUTs):
  - **Route:** Validate that path `uuid` and body `uuid` match (return **400 Bad Request** if not). Convert the request DTO to an entity via the factory, call the service update function with that entity, then map the returned entity to the response DTO. The route must **not** fetch by UUID or handle 404; the service does that.
  - **Factory:** The PUT request → entity factory function takes only the DTO (e.g. `put_dto_to_entity(dto: PutXxxRequest) -> Entity`). It returns an entity with `uuid`, and updatable fields (e.g. `name`, `description`) but **no** `id` (leave `id` unset / `None`). The factory must not take a session or existing entity; it only maps DTO → entity.
  - **Service:** The update function (e.g. `update_dummy(session, entity)`) accepts an entity. If the entity has **no** `id`, the service fetches the existing row by `entity.uuid`; if not found, it raises `AppException(ErrorCode.<RESOURCE>_NOT_FOUND)` so the app handler returns **404**. If found, the service builds an entity with the resolved `id` and `uuid` plus the incoming updatable fields, then performs the update (e.g. merge and commit). If the entity already has an `id`, the service performs the update as usual. This keeps "resolve by UUID or fail" inside the service; the route stays validation + convert + call + respond.
- **Database connection:** Configured by an optional `DATABASE_URL` environment variable. When unset or empty/whitespace, the application uses SQLite in-memory (`sqlite://`). When set, the URL is used as-is after validation at startup; the appropriate driver (e.g. PyMySQL for MariaDB) must be in dependencies. Special characters (e.g. `@`, `:`, `/`, `%`) used within any component of `DATABASE_URL` must be percent-encoded where applicable.
- **Session management:** `get_session()` is a generator yielding `Session` instances, injected into routes via `Depends(get_session)`. Tests override this dependency with a test-scoped SQLite session.
- **Schema management:** Table creation is a **local/dev-only** feature. The application runs `SQLModel.metadata.create_all(engine)` in the lifespan **only when the effective database is SQLite** (e.g. no `DATABASE_URL` or `sqlite://`). For any other backend (e.g. MariaDB in Compose or production), the app does not create or alter tables; schema is provided by the environment (e.g. MariaDB’s native init via `compose/mariadb/init/schema.sql`). No migration tool (Alembic) is in scope.

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
- `entra`: `EntraExternalAuthProvider` validates bearer JWT (signature via JWKS, standard claims, issuer, optional audience), maps claims to `Principal`, and supports client_credentials and OBO token acquisition for outbound OAuth use cases.

**Role model:** `Role` is a `StrEnum` with members `ADMIN`, `WRITER`, `READER`. `RoleMappingProvider.to_external(role_name)` maps internal labels to external identifiers. `BasicRoleMappingProvider` is an identity mapping.

**Dependencies:**

- `require_auth` — ensures a valid `Principal` exists (any authenticated user).
- `require_role(Role.XXX)` — returns a dependency that additionally checks the principal has the required role.

**Error sanitization:** Auth failures raise `AppException(ErrorCode.UNAUTHORIZED)` or `AppException(ErrorCode.FORBIDDEN)`. Provider-specific details are logged server-side only, never exposed to clients.

**Factory:** `build_auth_facade(settings)` in `auth/factory.py` selects the provider based on `AUTH_TYPE`.

### 11. Profile and Service Contracts

Service implementations are decoupled from the rest of the application by a **service contract** (interface). Which implementation is used at runtime is driven by an optional **profile** environment variable, enabling mock implementations for local or profile-based testing without touching the database or external systems.

**Profile:**

- **Environment variable:** `PROFILE` (optional). Values: `"default"` | `"mock"`. Default when unset: `"default"`.
- **Semantics:** `default` — wire the real (e.g. database-backed) implementation for each service. `mock` — wire the mock implementation for each service (in-memory or hard-coded data; no database or external calls).
- **Configuration:** `profile` is a typed field on `AppSettings` (e.g. `Literal["default", "mock"]`). See `.env.example` for reference.

**Service contract pattern:**

- **Contract:** For each logical service (e.g. dummies CRUD), define an abstract contract: an ABC (or `typing.Protocol`) in a dedicated module (e.g. `services/contracts/dummy_service.py`). The contract declares the methods that routes and other code depend on (e.g. `get_all`, `create`, `update`), with signatures using entity types and `Session` where the default implementation needs it; mock implementations may ignore the session.
- **Default implementation:** One concrete implementation that satisfies the contract and uses the real backend (e.g. database). Lives in `services/v{n}/implementations/` or equivalent (e.g. `default_dummy_service.py`). This is the implementation used when `profile == "default"`.
- **Mock implementation:** One concrete implementation that satisfies the same contract but returns data without connecting to the database or external systems (in-memory list, hard-coded entities, or similar). Lives alongside the default implementation (e.g. `mock_dummy_service.py`). Used when `profile == "mock"`.
- **Factory:** Factory functions (e.g. `build_dummy_service_v1(settings) -> DummyServiceV1Contract`, `build_dummy_service_v2(settings) -> DummyServiceV2Contract`) that, based on `settings.profile`, return the appropriate implementation. Factories live in `services/factory.py`. The app wires the returned instance into the dependency graph (e.g. `Depends(get_dummy_service_v1)` / `Depends(get_dummy_service_v2)`).
- **Wiring:** Routes and other consumers depend on the **contract type** (e.g. `DummyServiceV1Contract`, `DummyServiceV2Contract`), not on a concrete class. They receive the implementation chosen by the factory so that tests can override the dependency with a mock or a test double.

**Application-wide rule:** Every service that encapsulates business logic or data access has (1) a contract, (2) a default implementation, (3) a mock implementation, and (4) a factory that selects by `profile`. New services must follow this pattern.

### 12. Containerization

**Dockerfile:** Multi-stage. Builder uses `uv` (copied from `ghcr.io/astral-sh/uv:0.10.7`) to resolve and install locked dependencies. Runtime uses `python:3.14-slim` with a non-root `app` user. No dev dependencies in the final image.

IMPORTANT: the **Docker Compose** project (`compose/docker-compose.yaml`) is merely for local testing purposes, its technologies and components are not to be considered part of the product itself - this application is meant to be installed _anywhere_ as a container.

### 13. Testing

- **Framework:** pytest with `testpaths=["tests"]` and `pythonpath=["src"]`.
- **Database:** SQLite in-memory with `StaticPool`. Tests override `get_session` via `app.dependency_overrides`.
- **Auth in tests:** `AUTH_TYPE=none` is set via `os.environ.setdefault` in `tests/conftest.py`. Auth integration tests in `tests/auth/` use a synthetic IdP: test-generated RSA keypair, JWKS fixture, JWT signing helper, monkeypatched HTTP calls.
- **Rate limiting:** `limiter.reset()` is called in the client fixture to prevent cross-test pollution.
- **Coverage target:** >90%.
- **Test organization mirrors source:** `tests/api/`, `tests/auth/`, `tests/core/`, `tests/services/`, `tests/aop/`, `tests/observability/`.

### 14. Code Quality

Type checking is enforced with Astral's ty, targeting the project's Python version (3.14). Code quality is enforced by three commands: **ruff check**, **ruff format --check**, and **ty check**. Quality checks are defined as: running these three commands plus the full test suite; all must pass before commit.

**Ruff** is configured in `pyproject.toml`:

- `target-version = "py314"`
- `line-length = 88`
- Lint rules: `E`, `W`, `F`, `I`, `N`, `UP`, `B`, `SIM`, `TCH`
- `extend-immutable-calls = ["fastapi.Depends", "Depends"]`
- `known-first-party = ["fastapi_archetype"]`

**ty** is configured in `pyproject.toml` under `[tool.ty]` with `python-version = "3.14"` and `include = ["src", "tests"]`.

### 15. Cookiecutter Scaffolding

`scripts/build_template.py` generates a new project in one shot. Internally it builds a Cookiecutter template in a temporary directory (applying text substitutions, directory renames, and archetype-specific exclusions), invokes `cookiecutter --no-input`, and delivers the result to the user-specified output directory.

The generated template includes a `hooks/post_gen_project.py` that optionally strips the Dummy CRUD demo when `--no-demo` is passed, reusing the same removal logic as `scripts/remove_demo.py`.

**CLI flags:** `-n`/`--name` (required), `-o`/`--output` (required), `--description`, `--author`, `--email`, `--no-demo`, `--force`.

**Usage:**

```bash
python3 scripts/build_template.py -n "Order Service" -o ~/projects
```

## Conventions and Patterns

### DTO naming (mandatory)

Web DTOs **must** follow this pattern: **`<Method><Resource><Request | Response>`**

- **Method:** HTTP method in PascalCase (e.g. `Get`, `Post`, `Put`, `Patch`, `Delete`).
- **Resource:** Plural resource name in PascalCase, matching the API path (e.g. `Dummies` for `/dummies`).
- **Suffix:** `Request` for request bodies, `Response` for response bodies.

**Examples:** `PostDummiesRequest` (body for `POST /dummies`), `GetDummiesResponse` (item shape for `GET /dummies` or single-item response), `PostDummiesResponse` (body of `POST /dummies` response). Do not name DTOs after the entity (e.g. avoid `DummyCreate`, `DummyResponse`).

### Module organization

- One entity per file in `models/entities/` (SQLModel, table=True). One resource’s DTOs per file in `models/dto/<version>/` (e.g. `v1/`), using the `<Method><Resource><Request|Response>` naming pattern. One factory module per entity in `factories/` (entity ↔ DTO using Pydantic only).
- One resource's routes per file in `api/v{n}/`. Routes use DTOs for request/response and call factory functions to convert to/from entities. Routes depend on service **contracts** via DI (e.g. `Depends(get_dummy_service_v1)` / `Depends(get_dummy_service_v2)`), not on concrete service modules.
- **Service contracts:** One contract (ABC or Protocol) per logical service in `services/contracts/`. The contract defines the methods used by routes (accept/return entities; session passed where the default implementation needs it).
- **Service implementations:** For each contract, a default implementation (real backend) and a mock implementation (no DB/external calls) in `services/v{n}/implementations/` (e.g. `default_dummy_service.py`, `mock_dummy_service.py`). A factory in `services/factory.py` (or equivalent) selects by `settings.profile` and is used by the DI dependency.
- One resource's service module in `services/v{n}/` may re-export or wrap the implementation chosen by the factory; consumers depend on the contract type.
- The version router `__init__.py` aggregates resource routers.
- `services/__init__.py` aggregates AOP logging application (applied to implementation modules).

### Constants

- All resource paths, names, and descriptions are `ResourceDefinition` instances in `core/constants.py`.
- `HEALTH_PATH` is a plain string constant.
- No string literals for paths or resource names in route/service code.

### Configuration

- Every configurable value is a typed field on `AppSettings`.
- Environment variable names match field names in UPPER_CASE.
- Defaults are provided for all fields except auth-specific fields required when `AUTH_TYPE=entra`.
- **Profile:** Optional `PROFILE` with values `"default"` | `"mock"` (default `"default"`) drives which service implementation is wired (see §11 Profile and Service Contracts).

### Error handling

- All error codes live in the `ErrorCode` enum.
- Application code raises `AppException(ErrorCode.XXX, detail=...)`.
- Auth code raises `AuthError` subclasses internally; `dependencies.py` catches and translates them to `AppException`.
- Never return raw `JSONResponse` for error cases.

### Dependency injection

- Database sessions: `Depends(get_session)`.
- Auth: `Depends(require_auth)` or `Depends(require_role(Role.XXX))`.
- **Services:** Routes depend on the service contract via a dependency that calls the factory (e.g. `Depends(get_dummy_service_v1)` or `Depends(get_dummy_service_v2)`). The factory uses `settings.profile` to return the default or mock implementation. Consumers depend on the contract type, not the concrete class.
- Rate limiting: `@limiter.limit(settings.rate_limit_xxx)` decorator.
- All DI-based dependencies are overridable in tests via `app.dependency_overrides`.

### Testing

- Every new route needs endpoint tests in `tests/api/`.
- Every new service needs unit tests in `tests/services/`.
- Use the existing `client` and `session` fixtures from `tests/conftest.py`.
- Auth-related tests go in `tests/auth/` and use the synthetic IdP fixtures from `tests/auth/conftest.py`.
- Service and route tests may override the service dependency (e.g. with the default implementation and a session) or set `PROFILE`; see §11 Profile and Service Contracts.

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
- Do not add Alembic or database migration tooling — local schema via `create_all` (SQLite only); other backends use their own init (e.g. `compose/mariadb/init/schema.sql`).
- Do not add a local token-issuance endpoint — auth is external IdP only.
- Do not add libraries not listed in the technology stack without human approval.
- Do not add code comments that merely narrate what the code does.
- Do not skip `from __future__ import annotations` in new modules.
- Do not modify `tests/conftest.py` fixtures to be resource-specific — they are generic by design.
- Do not name web DTOs after the entity (e.g. `DummyCreate`, `WidgetResponse`) — use the mandatory pattern `<Method><Resource><Request|Response>` (e.g. `PostDummiesRequest`, `GetDummiesResponse`).
- Do not wire routes directly to concrete service classes — use the service contract and a profile-driven factory (see §11 Profile and Service Contracts).
- Do not add a new service without a contract, a default implementation, and a mock implementation — the pattern is mandatory for all services.

## Adding a New Resource

To add a new resource (e.g., `Widget`):

1. **Entity:** Create `models/entities/widget.py` with `class Widget(SQLModel, table=True)`, camelCase alias config, and `__tablename__`. This is the ORM model only; it is not used as a FastAPI request/response model. For resources that need a stable, client-facing identifier, add a `uuid` field (string, UUID format) on the entity.
2. **DTOs:** Create `models/dto/v1/widget.py` with Pydantic models following the **`<Method><Resource><Request|Response>`** naming pattern (e.g. `PostWidgetsRequest`, `GetWidgetsResponse`, `PostWidgetsResponse`). Same camelCase behaviour as existing DTOs. Response DTOs must include `uuid` (when the entity has one) and **must not** include the internal `id`.
3. **Factory:** Create `factories/widget.py` with `entity_to_dto(entity) -> GetWidgetsResponse` (or the appropriate response type) and `dto_to_entity(dto: PostWidgetsRequest) -> Widget` using only Pydantic (`model_validate`, `model_dump`). For update (PUT): add `put_dto_to_entity(dto: PutWidgetsRequest) -> Widget` that returns a `Widget` with `uuid` and updatable fields from the DTO but **no** `id` (see **Update-by-UUID pattern** in §2 Data Persistence). The service will resolve by UUID when `id` is missing.
4. **Constant:** Add `WIDGETS = ResourceDefinition(...)` to `core/constants.py`.
5. **Service contract:** Create `services/contracts/widget_service.py` with an ABC (e.g. `WidgetServiceV1Contract`) declaring the methods used by routes (e.g. `get_all`, `create`, `get_by_uuid`, `update` with entity types and `Session` where needed).
6. **Default implementation:** Create `services/v1/implementations/default_widget_service.py` with a class (e.g. `DefaultWidgetServiceV1`) implementing the contract with real database access. For update: when `entity.id` is None, fetch by `entity.uuid`; if not found, raise `AppException(ErrorCode.WIDGET_NOT_FOUND)`; otherwise resolve and update (see **Update-by-UUID pattern** in §2 Data Persistence).
7. **Mock implementation:** Create `services/v1/implementations/mock_widget_service.py` with a class (e.g. `MockWidgetServiceV1`) implementing the same contract with static or hard-coded data (no database or external calls).
8. **Factory and DI:** Add `build_widget_service_v1(settings) -> WidgetServiceV1Contract` in `services/factory.py` that returns the default or mock implementation based on `settings.profile`. Expose a dependency (e.g. `get_widget_service_v1`) used by routes via `Depends(get_widget_service_v1)`.
9. **AOP:** Import and `apply_logging()` the implementation modules in `services/__init__.py`.
10. **Routes:** Create `api/v1/widget_routes.py` with `APIRouter(prefix=WIDGETS.path, tags=[WIDGETS.name])`. Use DTOs for request body and response model; call factory to convert request DTO → entity for service and entity → response DTO for responses. Rate limits and auth as needed. **If the resource supports PUT (update):** use a path like `PUT /v1/widgets/{uuid}` and a request body that includes `uuid` plus updatable fields. In the route: validate that path `uuid` and body `uuid` match (return **400 Bad Request** if not); call the factory to convert the body DTO to an entity (no `id`); call the service update function with that entity; map the returned entity to the response DTO. Do **not** fetch by UUID or handle 404 in the route — the service does that (see **Update-by-UUID pattern** in §2 Data Persistence).
11. **Router registration:** Include the widget router in `api/v1/__init__.py`.
12. **Tests:** Add `tests/api/test_widget_routes.py` and `tests/services/v1/test_widget_service.py` (and tests for mock vs default behaviour when appropriate) using existing fixtures. Service tests may target the default implementation or the contract with a mock implementation override.
13. **Custom metrics (if needed):** Add counters to the `Counters` dataclass in `observability/prometheus.py`.
14. **Rate limits (if needed):** Add `rate_limit_get_widgets` / `rate_limit_post_widgets` fields to `AppSettings` and corresponding entries to `.env.example`.

The new resource automatically inherits OpenTelemetry tracing, Prometheus HTTP metrics, structured error handling, and the configured auth mode.
