# Project Context Analysis

## Requirements Overview

**Functional Requirements:**

28 FRs across 8 capability areas, all centered on proving that enterprise-grade cross-cutting concerns integrate coherently in a single FastAPI application:

| Category | FRs | Architectural Implication |
|---|---|---|
| REST API | FR1–FR4 | Thin route layer; JSON-only; structured error responses with centralized codes |
| Data Persistence | FR5–FR7 | SQLModel single-model pattern couples ORM and API schema; MariaDB target with SQLite test fallback |
| Configuration Management | FR8–FR9 | Startup-time .env loading with fail-fast validation; no lazy config discovery |
| API Documentation | FR10–FR12 | Zero-effort — FastAPI's built-in OpenAPI generation; Swagger at /docs, ReDoc at /redoc |
| Testing | FR13–FR16 | Unit tests mock externals; integration tests use SQLite in-memory; >90% coverage target |
| AOP Logging | FR17–FR19 | Module-level programmatic wrapping of function I/O and exceptions across a designated package without per-function annotation |
| Observability | FR20–FR23 | Dual instrumentation: OTEL traces for distributed tracing + Prometheus metrics at /metrics for scraping |
| Containerization | FR24–FR25 | Dockerfile producing a self-contained image; .env is the only external input |
| Code Organization | FR26–FR28 | Centralized constants, error codes/messages, and optional structured resource objects |

**Non-Functional Requirements:**

10 NFRs driving structural and quality decisions:

- **Code Quality (NFR1–NFR5):** Linter-enforced style, logical project structure, clean separation of capability areas, no dead code, comments only for non-obvious intent
- **Portability (NFR6–NFR7):** Docker image runs on Linux and macOS; no host-specific dependencies beyond pyproject.toml and .env
- **Developer Experience (NFR8–NFR10):** Project structure self-documenting; /dummies resource serves as copy-and-adapt pattern for new resources; sensible defaults minimize setup

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
