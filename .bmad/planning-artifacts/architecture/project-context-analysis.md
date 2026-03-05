# Project Context Analysis

## Requirements Overview

**Functional Requirements:**

The current PRD requirement inventory spans core and expansion capabilities, centered on proving that enterprise-grade cross-cutting concerns integrate coherently in a single FastAPI application:

| Category | FRs | Architectural Implication |
|---|---|---|
| REST API | FR1–FR4, FR29 | Thin route layer; JSON-only; structured error responses with centralized codes |
| Data Persistence | FR5–FR7, FR5a | SQLModel single-model pattern couples ORM and API schema; MariaDB target with SQLite default/test fallback |
| Configuration Management | FR8–FR9 | Startup-time .env loading with fail-fast validation; no lazy config discovery |
| API Documentation | FR10–FR12 | Zero-effort — FastAPI's built-in OpenAPI generation; Swagger at /docs, ReDoc at /redoc |
| Testing | FR13–FR16, FR40 | Unit/integration coverage with synthetic IdP path coverage for `entra` auth |
| AOP Logging | FR17–FR19, FR17a | Module-level programmatic wrapping of function I/O and exceptions across a designated package without per-function annotation |
| Observability | FR20–FR23, FR23a | Dual instrumentation: OTEL traces + Prometheus metrics with a custom business-metric pattern |
| Containerization | FR24–FR25 | Dockerfile producing a self-contained image; .env is the only external input |
| Code Organization | FR26–FR28 | Centralized constants, error codes/messages, and optional structured resource objects |
| API Versioning | FR37–FR38 | URL-prefix versioning for business endpoints while infra endpoints remain unversioned |
| Rate Limiting | FR30–FR32 | Per-endpoint throttling via environment configuration and standard 429 behavior |
| Authentication & Authorization | FR33–FR36, FR39, FR41 | External IdP integration, RBAC, safe client errors, and pluggable role mapping |
| Structured Logging | FR42–FR49 | Standards-first logging with `LOG_MODE`, `traceId` correlation, exception-mode rendering, and baseline redaction |

**Non-Functional Requirements:**

The NFR inventory now includes baseline quality attributes plus dedicated logging quality attributes:

- **Code Quality (NFR1–NFR5):** Linter-enforced style, logical project structure, clean separation of capability areas, no dead code, comments only for non-obvious intent
- **Portability (NFR6–NFR7):** Docker image runs on Linux and macOS; no host-specific dependencies beyond pyproject.toml and .env
- **Developer Experience (NFR8–NFR10):** Project structure self-documenting; /dummies resource serves as copy-and-adapt pattern for new resources; sensible defaults minimize setup
- **Logging Quality (NFR11–NFR15):** low-overhead operation, fault-tolerant logging behavior, consistent formatting semantics, environment-driven mode switching, and baseline secret redaction

**Scale & Complexity:**

- Primary domain: API backend (REST/FastAPI)
- Complexity level: Low (trivial domain; integration breadth is the challenge)
- Estimated architectural components: ~8 (routes, models, config, AOP, OTEL instrumentation, Prometheus instrumentation, error handling, testing infrastructure)

## Technical Constraints & Dependencies

- **Runtime:** Python 3.14 — library compatibility must be verified early
- **ORM:** SQLModel (implies SQLAlchemy underneath) — single model definition for both ORM and Pydantic validation
- **Database:** MariaDB (production), SQLite in-memory (tests) — ORM abstraction must handle both without conditional logic in application code
- **Dependency management:** uv (pyproject.toml + uv.lock)
- **AOP:** Plain Python decorators first; wrapt only if plain decorators prove insufficient
- **Observability:** OpenTelemetry SDK + prometheus-fastapi-instrumentator — two independent instrumentation systems sharing the request lifecycle
- **External services assumed available in MVP:** MariaDB, OTEL collector (optional — traces emitted but collector not required for MVP success)

## Cross-Cutting Concerns Identified

| Concern | Scope | Architectural Impact |
|---|---|---|
| AOP function logging | All functions in designated package | Module-level `apply_logging(module)` function wraps all public functions at startup; targets `services/` |
| OTEL tracing | Incoming HTTP requests | Middleware-level instrumentation; trace context propagation |
| Prometheus metrics | HTTP request count, latency, status | Middleware-level instrumentation via instrumentator library |
| Configuration validation | Application startup | Fail-fast boot sequence; all components depend on validated config |
| Centralized error handling | All endpoints | Consistent error response format; exception handlers at framework level |
| Dual-database abstraction | Data layer | Engine/session factory must be swappable; no dialect-specific code in application logic |
