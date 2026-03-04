# Architectural Decisions

This document records every architectural decision (AD) made during the design and implementation of fastapi-archetype, covering the initial architecture phase and subsequent implementation epics.

## AD 01 - Project Initialization Strategy

**Context:** The project needed a starting point. Several FastAPI boilerplate templates existed, but the project's purpose is to demonstrate how enterprise capabilities integrate from scratch.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| uvicorn-poetry-fastapi-project-template | - Pre-wired Docker and Uvicorn | - Poetry-based, not uv - Missing SQLModel, OTEL, Prometheus |
| fastapi-modular-boilerplate | - Covers async SQLAlchemy, Alembic, JWT, CI | - Over-scoped; heavy pruning defeats the purpose of a reference implementation |
| FastLaunchAPI-style enterprise templates | - Full SaaS feature set | - Fundamentally different use case (Celery, Stripe, OAuth2) |
| Clean `uv init` | - Full control over every dependency and structure - Every decision is intentional and documented | - More initial effort |

**Decision and justification:** Clean `uv init`. The project IS the reference implementation — its value lies in demonstrating integration from zero. Using a third-party template would import unwanted patterns, require pruning, and undermine the project's purpose as a proven-from-scratch archetype.

## AD 02 - ORM and Database Driver

**Context:** The application needs an ORM for database access and a MariaDB driver for production. The model definitions also serve as the API validation schema.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| SQLModel + PyMySQL | - Single model definition for ORM and Pydantic validation - PyMySQL is pure Python with zero system dependencies - Simplest Docker story | - PyMySQL is slower than C-based drivers - SQLModel is younger than raw SQLAlchemy |
| SQLAlchemy + Pydantic separately + mysqlclient | - Mature, battle-tested ORM - mysqlclient is faster | - Duplicate model definitions (ORM + schema) - mysqlclient requires system libraries (`libmysqlclient-dev`), complicating Docker builds |
| SQLAlchemy + Pydantic separately + aiomysql | - Async-native driver | - Duplicate model definitions - aiomysql maintenance has been inconsistent - Async not needed for a reference implementation |

**Decision and justification:** SQLModel with PyMySQL. SQLModel eliminates the dual-model problem (one class serves both ORM and API validation). PyMySQL's pure-Python nature means zero system dependencies and the simplest possible Docker image. Performance is irrelevant for a reference implementation.

## AD 03 - Configurable Database Driver with SQLite Default

**Context:** Requiring MariaDB for local development creates friction. A developer cloning the project should be able to run it immediately.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Always require MariaDB | - Production parity | - Requires Docker or local MariaDB just to start the app - Poor developer experience |
| SQLite in-memory as default, MariaDB via config toggle | - Zero-setup development - Developer can exercise the full API immediately - Same ORM code; only engine config changes | - SQLite has dialect differences - In-memory data is lost on restart |
| Embedded database (e.g., DuckDB) | - More feature-complete than SQLite | - Unnecessary complexity - Not a standard Python pattern |

**Decision and justification:** SQLite in-memory as the default via `DB_DRIVER=sqlite`, with `DB_DRIVER=mysql+pymysql` for MariaDB. The `StaticPool` and `check_same_thread=False` settings make SQLite work correctly with FastAPI's thread pool. No dialect-specific code exists in application logic — the abstraction is handled entirely at the engine configuration level.

## AD 04 - Database Session Management

**Context:** Every route that accesses the database needs a session. The pattern must support clean test database swapping without modifying route code.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| FastAPI `Depends()` with generator | - Idiomatic FastAPI - Session lifecycle managed by framework - Tests override via `app.dependency_overrides` | - Requires understanding of FastAPI DI |
| Middleware-injected session (request.state) | - Transparent to route handlers | - No type safety - Harder to test - Session lifecycle less explicit |
| Manual session creation in routes | - Simple, explicit | - Repeated boilerplate - No clean test override mechanism |

**Decision and justification:** FastAPI `Depends()` with a generator function (`get_session`). This is the idiomatic FastAPI pattern and enables clean test database swapping via dependency overrides without touching any route code.

## AD 05 - Schema Management Strategy

**Context:** The application needs database tables created. The question is whether to use a migration tool.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| SQLModel `create_all` | - Zero configuration - No migration files to manage - Appropriate for single-table MVP | - No migration history - No rollback capability - Manual intervention for schema changes |
| Alembic migrations | - Production-grade schema evolution - Rollback support - Migration history | - Adds complexity for a single-table reference implementation - Alembic configuration and migration files |

**Decision and justification:** `SQLModel.metadata.create_all(engine)` in the application lifespan. The project has a single table (`DUMMY`) serving as a demonstration resource. Migration tooling would add complexity without proportional value. Alembic remains a natural extension point but is explicitly out of scope.

## AD 06 - Configuration Management

**Context:** The application needs to load and validate configuration from the environment and `.env` files, failing fast on invalid values.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| pydantic-settings `BaseSettings` | - Native Pydantic integration - Auto `.env` loading - Typed validation with fail-fast semantics - Field validators for custom rules | - Tightly coupled to Pydantic ecosystem |
| python-dotenv + manual parsing | - Lightweight, no framework dependency | - No type safety - Manual validation code - Error-prone |
| dynaconf | - Multi-format support (TOML, YAML, env) - Environment layering | - Additional dependency - More complex than needed |

**Decision and justification:** pydantic-settings `BaseSettings`. It provides typed fields, automatic environment variable binding, `.env` file loading, and fail-fast validation at startup — all with minimal code. Every configurable value is a field on `AppSettings`.

## AD 07 - Structured Error Handling

**Context:** All error responses must follow a consistent JSON structure. Error codes and messages need a single source of truth.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Enum-based registry + `AppException` + global exception handlers | - Type-safe, IDE-friendly - Single source of truth for all error codes - Consistent response format across the application | - Requires custom exception class and handlers |
| FastAPI `HTTPException` subclasses | - Built into the framework | - No centralized error code registry - Inconsistent response format across different exception types |
| Per-route try/except with JSONResponse | - Explicit per-route error handling | - Duplicated error formatting logic - Easy to drift from a consistent format |

**Decision and justification:** Enum-based error registry (`ErrorCode`) where each member carries `(code, message, http_status)`, a custom `AppException`, and global exception handlers for `AppException`, `RateLimitExceeded`, and `RequestValidationError`. All error responses use the shape `{"errorCode", "message", "detail"}`.

## AD 08 - Package Structure

**Context:** The project structure must make each capability independently locatable and support AOP decoration of a designated package.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Layered by technical concern (`api/`, `models/`, `core/`, `services/`, `aop/`, `observability/`) | - Each capability is independently locatable - Clear AOP target (services/) - Familiar to most Python developers | - Can become deep for large applications |
| Domain-driven (feature folders) | - Co-locates related code | - Unclear AOP target - Cross-cutting concerns don't fit neatly into feature folders |
| Flat (all modules at package root) | - Simple | - Does not scale - No clear boundaries |

**Decision and justification:** Layered structure with `src/` layout. The `api/` layer handles HTTP concerns, `services/` contains business logic (and is the AOP target), `models/` holds SQLModel definitions, `core/` centralizes configuration, constants, errors, and database setup, `aop/` and `observability/` isolate cross-cutting concerns.

## AD 09 - AOP Function Logging Mechanism

**Context:** All service-layer functions should be automatically logged (inputs and return values) without modifying each function individually. The PRD specifies plain Python decorators first, falling back to `wrapt` only if necessary.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Plain Python decorator (`functools.wraps`) + `apply_logging(module)` | - No external dependency - `apply_logging` wraps all public functions in a module at import time - Clean separation: services code is never modified | - No exception-path logging - No idempotency guard |
| `wrapt` decorator library | - Handles edge cases (classmethods, descriptors) - Preserves introspection better | - External dependency - Not needed for plain functions |
| `aspectlib` | - Full AOP framework with pointcuts | - Heavy dependency for a simple use case - Less Pythonic |

**Decision and justification:** Plain Python decorators with `functools.wraps`. The `log_io` decorator logs at DEBUG level, and `apply_logging(module)` wraps all public functions in a target module. Only functions whose `__module__` matches the target are wrapped (re-exported imports are skipped). `wrapt` was not needed — plain decorators proved sufficient for the service-layer use case.

## AD 10 - Logging Configuration

**Context:** The application needs a configured logging subsystem with output to stdout and a configurable log level.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| stdlib `logging.basicConfig` | - No external dependency - Single configuration point in lifespan - `force=True` reconfigures even if uvicorn pre-configured the root logger | - Basic formatting options |
| structlog | - Structured JSON logging - Processor pipeline | - Additional dependency - More complex setup |
| loguru | - Simpler API - Auto-formatting | - Additional dependency - Replaces stdlib patterns |

**Decision and justification:** stdlib `logging.basicConfig` called in the application lifespan with `LOG_LEVEL` from settings, `sys.stdout` as destination, and `force=True`. Modules obtain loggers via `logging.getLogger(__name__)`. No additional logging library is needed.

## AD 11 - OpenTelemetry Tracing Integration

**Context:** The application needs distributed tracing for all HTTP requests with optional export to an OTEL collector.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Programmatic SDK setup with `FastAPIInstrumentor` | - Full control over configuration - Toggle export via `OTEL_EXPORT_ENABLED` - No overhead when export is disabled (no processor added) | - More setup code than zero-code |
| `opentelemetry-distro` zero-code instrumentation | - Minimal code | - Less control over configuration - Environment variable-driven (conflicts with pydantic-settings pattern) |
| No tracing | - Simplest | - Defeats the project's purpose of demonstrating observability |

**Decision and justification:** Programmatic SDK setup. A `setup_otel(app, settings)` function configures a `TracerProvider`, optionally adds a `BatchSpanProcessor` with `OTLPSpanExporter` (gRPC) when export is enabled, and instruments the app via `FastAPIInstrumentor`. The `/metrics` endpoint is excluded from tracing. gRPC was chosen over HTTP as the standard OTLP transport. The OTEL Collector uses the `contrib` distribution (not `core`) because the Jaeger and Prometheus exporters are only available in contrib.

## AD 12 - Prometheus Metrics

**Context:** The application needs HTTP request metrics auto-instrumented and a pattern for custom business metrics.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| `prometheus-fastapi-instrumentator` for HTTP metrics + `prometheus_client.Counter` for custom metrics | - Auto-instruments all HTTP requests with zero per-endpoint config - Custom metrics use the standard Prometheus client library directly - Both auto and custom metrics appear at `/metrics` via shared registry | - Two different APIs (instrumentator for auto, client for custom) |
| Manual `prometheus_client` middleware for everything | - Single API | - Significant boilerplate for HTTP metrics - Must instrument every endpoint manually |
| `starlette-prometheus` | - Starlette-native | - Less feature-complete - Smaller community |

**Decision and justification:** `prometheus-fastapi-instrumentator` for automatic HTTP metrics, with `prometheus_client.Counter` used directly for custom business metrics (e.g., `dummies_created_total`). Custom metrics are defined as fields on `Metrics`/`Counters` dataclasses in `observability/prometheus.py` and auto-register with the default collector registry. The `setup_prometheus` call is placed at module level (not in the lifespan) because `Instrumentator.instrument()` calls `add_middleware()`, which raises `RuntimeError` after app startup.

## AD 13 - API Versioning Strategy

**Context:** Business API endpoints need versioning to support future evolution without breaking existing clients.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| URL prefix (`/v1/`) via `APIRouter` | - Framework-native (FastAPI's `APIRouter(prefix="/v1")`) - Explicit in URLs - Clear routing - Adding v2 means creating a new router | - URL pollution - Not RESTful purist approach |
| Header-based (`Accept-Version: v1`) | - Clean URLs | - Not visible in browser - Harder to test and debug - Requires custom middleware |
| Query parameter (`?version=1`) | - Simple | - Non-standard - Clutters query string |

**Decision and justification:** URL prefix with nested `APIRouter`. The v1 router has `prefix="/v1"` and includes resource routers (e.g., dummy_router with `prefix="/dummies"`), producing `/v1/dummies`. Infrastructure endpoints (`/health`, `/metrics`, `/docs`, `/redoc`) remain at the root, unversioned. The version prefix is the router's concern, not the resource constant's — `DUMMIES.path` stays `"/dummies"`.

## AD 14 - Rate Limiting

**Context:** API endpoints need protection from abuse with configurable, per-endpoint rate limits.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| `slowapi` with per-endpoint decorators | - De facto FastAPI rate limiting library - Per-endpoint control via `@limiter.limit()` - Limit strings from settings, not hardcoded - Standard rate-limit response headers | - Requires `Request` parameter on every rate-limited endpoint |
| Custom ASGI middleware | - Full control | - Significant implementation effort - Reinventing the wheel |
| Reverse-proxy-level limiting (nginx, etc.) | - Offloads from application | - Not demonstrable in the application itself - Depends on infrastructure |

**Decision and justification:** `slowapi` with per-endpoint `@limiter.limit()` decorators reading thresholds from `AppSettings` (e.g., `RATE_LIMIT_GET_DUMMIES=100/minute`). A custom `RateLimitExceeded` handler returns the project's structured error format instead of slowapi's default. Rate limits are not applied to infrastructure endpoints.

## AD 15 - Authentication and Authorization Architecture

**Context:** The application needs authentication and authorization that integrates with enterprise identity platforms without implementing local credential management.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| External IdP with facade + provider abstraction, per-route `Depends()` | - No local token issuance or credential storage - Facade isolates provider-specific logic - `AUTH_TYPE=none` for frictionless local development - `require_auth` / `require_role` as explicit, composable route dependencies - Extensible: new providers need only implement the `AuthProvider` ABC | - More initial abstraction layers |
| Local JWT issuance with username/password | - Self-contained | - Security liability (credential storage) - Not enterprise-pattern - Out of scope for a reference implementation |
| Global authentication middleware | - Transparent to routes | - All-or-nothing (no selective endpoint protection) - Less explicit — harder to reason about which endpoints are protected |

**Decision and justification:** External IdP-first pattern with a facade/provider abstraction. `AuthProvider` (ABC) is implemented by `NoAuthProvider` (dev bypass) and `EntraExternalAuthProvider` (JWT validation, OAuth flows, Graph role enrichment). `AuthFacade` provides a single boundary. `build_auth_facade(settings)` wires the correct provider based on `AUTH_TYPE`. Protection is applied per-route via `Depends(require_auth)` or `Depends(require_role(Role.XXX))`, keeping it explicit and composable.

## AD 16 - JWT Validation Library

**Context:** The Entra auth provider needs to validate JWT bearer tokens, verify signatures against remote JWKS keys, and parse claims.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| `python-jose[cryptography]` | - Mature JWT library - `cryptography` backend for RSA/EC key handling - Supports JWK construction and signature verification | - Less actively maintained than PyJWT |
| `PyJWT` | - Most popular Python JWT library - Actively maintained | - JWK handling requires additional setup |
| `authlib` | - Full OAuth/OIDC toolkit | - Much larger dependency surface than needed |

**Decision and justification:** `python-jose[cryptography]`. It provides JWT parsing, JWK construction, and signature verification in a single package. The `cryptography` extra handles RSA key operations needed for Entra token validation. The library is already proven in FastAPI ecosystems.

## AD 17 - Auth Error Response Sanitization

**Context:** Auth failure responses could leak provider-specific details (discovery URIs, token endpoints, internal error messages) to API callers.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Generic client responses + server-side logging | - No provider internals exposed to clients - Detailed diagnostics available in server logs | - Harder to debug from the client side |
| Detailed error responses | - Easier client-side debugging | - Security risk: leaks infrastructure details |
| No special handling (propagate provider errors) | - Simple | - Exposes internal URIs, stack traces, and provider error messages |

**Decision and justification:** Generic client responses with server-side logging. All auth failures raise `AppException(ErrorCode.UNAUTHORIZED)` or `AppException(ErrorCode.FORBIDDEN)` with `detail=None`. Provider-specific error details are logged at WARNING level in `dependencies.py` before re-raising. Clients receive only the standard `ErrorCode` message.

## AD 18 - Role Mapping Provider Abstraction

**Context:** In enterprise IdP configurations, roles may be represented as GUIDs or other non-human-readable identifiers rather than plain names. The role check logic needs to bridge internal role labels to external identifiers.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Pluggable `RoleMappingProvider` contract | - Extensible: implementations can be env-based, table-based, or any other strategy - Wired via the existing factory pattern - Default identity mapping works out of the box | - Additional abstraction layer |
| Hardcoded role-to-GUID mapping in config | - Simple for a single IdP | - Not extensible - Couples mapping logic to configuration |
| Direct enum-to-string comparison | - Minimal code | - Breaks when external role identifiers differ from internal labels |

**Decision and justification:** A pluggable `RoleMappingProvider` ABC with `to_external(role_name: str) -> str`. `BasicRoleMappingProvider` implements identity mapping (returns the role name unchanged). `require_role` calls `facade.role_mapper.to_external(required_role.value)` before checking against the principal's roles. Custom implementations (e.g., GUID mapping) can be wired by updating the factory.

## AD 19 - ASGI Server

**Context:** The application needs an ASGI server to serve FastAPI in production.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Uvicorn standalone | - Standard FastAPI companion - Lightweight - Multi-worker scaling is a platform concern (Kubernetes, etc.) | - Single-worker by default |
| Uvicorn + Gunicorn | - Built-in multi-worker management | - Adds Gunicorn dependency - Multi-worker is a deployment concern, not an application concern |
| Hypercorn | - HTTP/2 support - Trio support | - Less common in FastAPI ecosystem - HTTP/2 not needed |

**Decision and justification:** Uvicorn standalone. It is the standard ASGI server for FastAPI. Multi-worker scaling is delegated to the container orchestration layer (e.g., Kubernetes pod replicas), not the application process manager.

## AD 20 - Containerization Strategy

**Context:** The application needs a Docker image that is production-ready, portable across Linux and macOS, and contains no build tools or dev dependencies.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Multi-stage Dockerfile with `python:3.14-slim` | - Clean separation of build and runtime - No build tools in final image - `slim` avoids Alpine musl issues with compiled dependencies - Non-root `app` user | - Larger than Alpine-based images |
| Alpine-based (`python:3.14-alpine`) | - Smallest image size | - musl libc compatibility issues with compiled Python packages - Requires build tools for some dependencies |
| Single-stage Dockerfile | - Simpler Dockerfile | - Build tools and dev dependencies in final image - Larger, less secure |

**Decision and justification:** Multi-stage Dockerfile with `python:3.14-slim`. The builder stage copies `uv` from the official image (`ghcr.io/astral-sh/uv:0.10.7`, pinned for reproducibility) and installs production dependencies via `uv sync --locked --no-dev --no-editable`. The runtime stage copies only the `.venv` and runs as a non-root `app` user.

## AD 21 - Docker Compose Observability Stack

**Context:** The Docker Compose environment needs a full observability stack so developers can verify traces and metrics end-to-end without external infrastructure.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| OTEL Collector (contrib) + Jaeger + Prometheus + Grafana | - Full observability pipeline: traces flow through OTEL Collector to Jaeger, metrics scraped by Prometheus, dashboards in Grafana - Contrib distribution includes Jaeger and Prometheus exporters | - Six services total; heavier resource usage |
| OTEL Collector (core) + Jaeger + Prometheus | - Lighter collector image | - Core distribution lacks Jaeger and Prometheus exporters; cannot route traces or expose collector metrics |
| Application-only (no observability services) | - Simplest compose file | - Cannot verify observability integration end-to-end |

**Decision and justification:** Full stack with OTEL Collector contrib distribution, Jaeger, Prometheus, and Grafana. The contrib distribution was required because the core OTEL Collector does not include the Jaeger exporter or Prometheus exporter. The stack enables end-to-end verification of the entire observability pipeline.

## AD 22 - Dependency Management and Build Tooling

**Context:** The project needs a dependency manager and build system for Python 3.14.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| uv | - Fast, unified Python tooling (venv, install, lock, build) - `pyproject.toml` + `uv.lock` for reproducibility - Same ecosystem as Ruff (Astral) | - Newer tool, smaller ecosystem |
| Poetry | - Mature, widely adopted - Built-in dependency resolution | - Slower than uv - Separate lock format - Not as well-integrated with modern Python packaging |
| pip + pip-tools | - Standard, minimal | - No built-in lock format - Manual virtual environment management - Slower resolution |

**Decision and justification:** uv. It provides fast dependency resolution, deterministic builds via `uv.lock`, and seamless integration with `pyproject.toml`. The `uv_build` backend is used for the build system. `uv sync`, `uv run`, and `uv add` cover the full developer workflow.

## AD 23 - Code Quality Tooling

**Context:** The project needs linting and formatting enforcement targeting Python 3.14.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| Ruff | - Single tool replacing flake8 + black + isort - Extremely fast (Rust-based) - Same ecosystem as uv (Astral) - Configured entirely in `pyproject.toml` | - Newer tool |
| flake8 + black + isort | - Industry standard, mature | - Three separate tools to configure and run - Slower |
| pylint | - Deep analysis, refactoring suggestions | - Very slow - Opinionated, high noise |

**Decision and justification:** Ruff with `target-version = "py314"` and rules E, W, F, I, N, UP, B, SIM, TCH. A single tool handles linting and formatting with the same configuration file. `extend-immutable-calls` is configured for `Depends` to suppress false positives.

## AD 24 - Test Infrastructure

**Context:** The test suite needs to run without external infrastructure, support database integration tests, and allow clean dependency overrides.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| pytest + SQLite in-memory + FastAPI dependency overrides | - No external infrastructure needed - `app.dependency_overrides[get_session]` swaps the database cleanly - Session-scoped engine (created once), per-test table drop/create for isolation - Auth integration tests use synthetic IdP (test-generated RSA keypair) | - SQLite dialect differences from MariaDB |
| pytest + dedicated test MariaDB (Docker) | - Full production parity | - Requires Docker running - Slower test execution - CI complexity |
| Mocking all database calls | - Fast, no database setup | - Does not test actual SQL behavior - Brittle mocks |

**Decision and justification:** pytest with SQLite in-memory and FastAPI dependency overrides. The test engine uses `StaticPool` and `check_same_thread=False`. Tables are dropped and recreated between tests for isolation. `AUTH_TYPE=none` is set via `os.environ.setdefault` in the root `conftest.py`. `limiter.reset()` prevents rate-limit state leakage between tests. Auth integration tests use a synthetic IdP with test-generated RSA keypairs and monkeypatched HTTP calls, verifying the full Entra code path without external infrastructure.
