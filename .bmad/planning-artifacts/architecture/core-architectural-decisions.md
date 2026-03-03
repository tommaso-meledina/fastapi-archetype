# Core Architectural Decisions

## Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- MariaDB driver selection (affects ORM configuration)
- Configuration management pattern (all components depend on config)
- Database session management (affects every route and test)
- Project package structure (affects all code organization)

**Important Decisions (Shape Architecture):**
- Error handling pattern (affects all endpoints)
- ASGI server (affects Dockerfile and runtime)
- Dockerfile strategy (affects deployment)
- Linting & formatting (affects developer workflow)

**Deferred Decisions (Post-MVP):**
- Authentication & authorization → Phase 3
- Rate limiting → Phase 3
- API versioning → Phase 3
- Database migrations (Alembic) → not in MVP scope; single-table schema managed via SQLModel `create_all`

## Data Architecture

| Decision | Choice | Version | Rationale |
|---|---|---|---|
| ORM | SQLModel | 0.0.37 | PRD-specified; single model definition for ORM + Pydantic validation |
| Database (prod) | MariaDB | — | PRD-specified |
| Database (dev default) | SQLite in-memory | — | Zero-setup local development; `DB_DRIVER=sqlite` (default) |
| Database (test) | SQLite in-memory | — | PRD-specified; self-contained test execution |
| MariaDB driver | PyMySQL | 1.1.2 | Pure Python; zero system dependencies; simplest Docker story; performance irrelevant for reference implementation |
| Session management | FastAPI `Depends()` with generator | — | Idiomatic FastAPI; enables clean test database swap via dependency override |
| Schema management | SQLModel `create_all` | — | Single-table MVP; no migration complexity warranted |

**Cascading implication:** The `Depends()` + generator pattern means database abstraction is handled through dependency injection and a configurable `DB_DRIVER` setting. `DB_DRIVER=sqlite` (default) uses SQLite in-memory with `StaticPool` for zero-setup local development; `DB_DRIVER=mysql+pymysql` connects to MariaDB for production. Tests override with SQLite via dependency injection. No dialect-specific code in application logic.

## Authentication & Security

Deferred to Phase 3 per PRD. No authentication, authorization, or security middleware in MVP scope.

## API & Communication Patterns

| Decision | Choice | Version | Rationale |
|---|---|---|---|
| API style | REST, JSON-only | — | PRD-specified |
| Documentation | FastAPI built-in OpenAPI 3.x, Swagger at `/docs`, ReDoc at `/redoc` | — | PRD-specified; zero-configuration |
| Error handling | Enum-based error registry + custom `AppException` + global exception handler | — | Satisfies FR27 (single central location); type-safe; IDE-friendly; consistent response format |
| Configuration | pydantic-settings `BaseSettings` | 2.13.1 | Native Pydantic integration; auto `.env` loading; typed validation; fail-fast at startup (FR8–FR9) |
| Logging configuration | `logging.basicConfig` with `LOG_LEVEL` setting | — | Stdlib only; single configuration point in lifespan; stdout destination; level defaults to INFO (FR17a) |

## Infrastructure & Deployment

| Decision | Choice | Version | Rationale |
|---|---|---|---|
| ASGI server | Uvicorn standalone | 0.41.0 | Standard FastAPI companion; multi-worker is a platform concern, not application concern |
| Containerization | Multi-stage Dockerfile, `python:3.14-slim` runtime | — | Clean separation of build and runtime; no build tools in final image; avoids Alpine musl issues |
| Dependency management | uv | — | Fast, unified Python tooling; `pyproject.toml` + `uv.lock` for reproducibility |
| Linting & formatting | Ruff | 0.15.4 | Replaces flake8 + black + isort; single tool; same ecosystem as uv (Astral) |
| Package structure | Layered | — | Separates by technical concern (api, models, core, services); clear AOP target; each capability independently locatable |

## Decision Impact Analysis

**Implementation Sequence:**
1. Project initialization (`uv init`) + package structure
2. Configuration management (pydantic-settings) — all components depend on this
3. Database layer (SQLModel + PyMySQL + session management)
4. REST endpoints (`/dummies` routes + error handling)
5. Configurable database driver (SQLite default for zero-setup dev)
6. AOP logging (decorators on services layer)
6a. Logging subsystem configuration (stdout handler, configurable level)
7. Observability (OTEL + Prometheus middleware)
8. Testing infrastructure (pytest + SQLite override)
9. Dockerfile (multi-stage build)
10. Linting & formatting (Ruff configuration)

**Cross-Component Dependencies:**
- Configuration → everything (all components read config at startup)
- Database session management → routes, tests (dependency injection pattern)
- Error registry → routes, exception handler (centralized codes)
- Package structure → AOP (designated package target), tests (import paths)
