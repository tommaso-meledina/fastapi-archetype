# Epic List

## Epic 1: Running Application with CRUD API
A developer can clone the project, run it immediately (SQLite in-memory by default), and interact with a fully working REST API — with structured error responses, centralized constants, auto-generated API docs at `/docs`, and a clear project structure that serves as a copy-and-adapt template. MariaDB is supported via a configuration toggle.
**FRs covered:** FR1–FR12, FR5a, FR26–FR29
**NFRs addressed:** NFR1–NFR5, NFR8–NFR10

## Epic 2: Cross-Cutting Function Logging (AOP)
A developer can see that all service-layer functions are automatically logged (inputs and return values) via a decorator mechanism applied at the package level — no per-function modification needed. The Python logging subsystem is configured at startup so that all log output reaches stdout with a configurable level.
**FRs covered:** FR17–FR19, FR17a

## Epic 3: Observability — Distributed Tracing and Metrics
A developer can see OpenTelemetry traces emitted for every request and Prometheus metrics exposed at `/metrics` — full observability with zero additional setup.
**FRs covered:** FR20–FR23

## Epic 4: Comprehensive Test Suite
A developer can run the complete test suite to verify all capabilities work together. Unit tests mock externals, integration tests use SQLite in-memory, and the suite achieves >90% code coverage.
**FRs covered:** FR13–FR16

## Epic 5: Production-Ready Containerization
A developer can build a Docker image and run the full application in a container with no configuration beyond the `.env` file. The image runs consistently across Linux and macOS.
**FRs covered:** FR24–FR25
**NFRs addressed:** NFR6–NFR7

## Epic 6: Docker Compose Development Environment
A developer can run `docker compose up` and get the full application running against MariaDB with traces flowing to an OTEL collector and metrics scraped by Prometheus — a complete production-like environment with no manual service setup.
**Phase:** 1 (Infrastructure)

## Epic 7: Custom Prometheus Metric Example
A developer can see a custom application-specific Prometheus metric (a business counter) exposed alongside the auto-instrumented HTTP metrics at `/metrics`, serving as a replicable pattern for adding domain-specific metrics.
**FRs covered:** FR23a
**Phase:** 2 (Expansion)

## Epic 8: API Versioning
A developer can see that all business API endpoints are organized under a versioned URL prefix (`/v1/`), while infrastructure endpoints remain at the root — a clear, framework-native pattern for future API versions.
**FRs covered:** FR37–FR38
**Phase:** 2 (Expansion)

## Epic 9: Rate Limiting
A developer can see per-endpoint rate limiting enforced on the API, with limits configurable via environment variables, standard rate-limit response headers, and a clear 429 error response.
**FRs covered:** FR30–FR32
**Phase:** 2 (Expansion)

## Epic 10: External IdP Authentication and Role-Based Access Control
A developer can see external IdP-backed bearer-token authentication and RBAC integrated with explicit route dependencies, including optional remote role enrichment and a development `AUTH_TYPE=none` mode.
**FRs covered:** FR33–FR36
**Phase:** 2 (Expansion)

## Epic 11: Auth/Authz Hardening
Auth subsystem refinements to improve production-readiness: sanitized error responses, validated auth behavior under realistic IdP simulation, and an extensible role-mapping contract for bridging internal role labels to external identity systems.
**FRs covered:** FR39–FR41
**Phase:** 2 (Expansion)

## Epic 12: Structured Logging with Trace Correlation
A developer can switch logging between enterprise-friendly plain text and NDJSON output using standard Python/FastAPI logging mechanisms, with consistent `traceId` correlation, unified exception handling behavior, and baseline sensitive-data redaction.
**FRs covered:** FR42–FR49
**NFRs addressed:** NFR11–NFR15
**Phase:** 3 (Refinement)

## Epic 13: Demo Removal
A developer who has cloned the archetype can run `python3 scripts/remove_demo.py` to strip all Dummy CRUD boilerplate — leaving a clean project with all infrastructure intact, structural scaffolding preserved, and all tests passing. Prerequisite: auth and observability tests are decoupled from specific resource endpoints.
**FRs covered:** FR50–FR56
**NFRs addressed:** NFR16–NFR17
**Phase:** 2 (Expansion)

## Epic 14: Token-Only Inbound RBAC with Graph Removal
A developer can enforce inbound authorization using token claims only (`roles`) with fail-closed behavior, while preserving `RoleMappingProvider` extensibility and fully removing Graph-based role retrieval and all associated zombie code paths.
**FRs covered:** FR1–FR11 (this request scope)
**NFRs addressed:** NFR1–NFR6 (this request scope)
**Phase:** 3 (Refinement)

## Epic 15: Separate Entity Models, Versioned DTOs, and Factories
A developer sees a clear separation between ORM entities (`models/entities/`), versioned web DTOs (`models/dto/v1/`, `v2/`, …), and a dedicated mapping layer (`factories/`) using Pydantic-only conversion, so that API and persistence can evolve independently.
**Phase:** 3 (Refinement)

## Epic 16: Entity UUID and PUT Dummies by UUID
A developer sees the Dummy entity expose a stable `uuid` (string) to clients while the internal ID is never returned; the dummies API supports PUT to update a Dummy by UUID, with path and body both carrying the UUID and returning 400 if they disagree; factory logic resolves UUID to entity/ID when mapping from DTO to entity for updates.
**Phase:** 3 (Refinement)

## Epic 17: Database URL Configuration
A developer configures the database via an optional `DATABASE_URL` environment variable; when unset, the application uses SQLite in-memory. When set, the URL is validated at startup and used as-is (the appropriate driver library must be in dependencies). Engine creation is split into a SQLite-specific path and a generic URL path, enabling plug-and-play with any SQLAlchemy-supported backend (PostgreSQL, Oracle, etc.) without code changes.
**Phase:** 3 (Refinement)

## Epic 18: Profile and Service Contracts (PoC via Dummies)
A developer can set an optional `PROFILE` env (`"default"` or `"mock"`); the dummies service is refactored behind a service contract with a default (database) and a mock (in-memory) implementation, wired by a profile-driven factory. Establishes the pattern for all services: contract, default impl, mock impl, factory, DI.
**Phase:** 3 (Refinement)

## Epic 19: Static Type Checking with Astral ty
A developer runs Astral's ty as part of quality gates; NFR1, architecture docs, and AD 23 are updated to require type checking; pyproject.toml, PROJECT_CONTEXT, README, and AGENTS.md document ty and define quality checks (ruff + ty + tests); the codebase passes `uv run ty check` with zero errors and zero warnings.
**NFRs addressed:** NFR1 (extension)
**Phase:** 3 (Refinement)

## Epic 20: Hygiene & Quick Wins
Small, mechanical fixes with no architecture changes: Docker env vars (`PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`), missing `tests/auth/__init__.py`, `_default_uuid` simplification, `kw_only=True` on dataclasses, `slots=True` removal, `Enum` for `log_level`, `ipdb` dev dep, `anyio` → `asyncio` test markers, uvicorn worker config.
**Source:** Peer review feedback (NEXT_STEPS.md actions 1–9)
**Phase:** 4 (Feedback)

## Epic 21: Python 3.14 Modernization & Model Cleanup
Align the codebase with Python 3.14 idioms and DRY up the model layer: remove `from __future__ import annotations`, remove `# noqa: TC001` suppressions, remove `TCH` ruff rule, replace `type: ignore` with `cast()`, introduce `CamelCaseModel` base using `pydantic.alias_generators.to_camel`, remove `alias_generator` from entities.
**Source:** Peer review feedback (NEXT_STEPS.md actions 10–16, 48)
**Phase:** 4 (Feedback)

## Epic 22: Configuration & Module Organization
Singleton config, cleaner module exports, task runner: implement `AppSettings` module singleton, replace all `AppSettings()` call sites, add `__all__` to key `__init__.py` files, add Justfile or Makefile.
**Source:** Peer review feedback (NEXT_STEPS.md actions 17–20)
**Phase:** 4 (Feedback)

## Epic 23: Logging Overhaul & Test Cleanup
Migrate to structlog and streamline the test suite: add `structlog` runtime dep, rewrite `observability/logging.py` with structlog processors, simplify `logging_decorator.py`, remove mock-implementation unit tests, exclude mock files from coverage, reorganize large test classes.
**Source:** Peer review feedback (NEXT_STEPS.md actions 21–26)
**Phase:** 4 (Feedback)

## Epic 24: Pythonic Redesign — Functions over Classes
Replace the Spring Boot-like provider/contract/facade/factory class hierarchy with idiomatic Python: plain functions, module namespaces, and dict-dispatch. Applies to both the auth subsystem and the service layer. This deliberately reverts Epic 18's structural choices while preserving profile-switching capability.
**Source:** Peer review feedback (NEXT_STEPS.md actions 27–39)
**Phase:** 4 (Feedback)

## Epic 25: Async Rewrite
Convert the entire request → service → DB path to async: `async def` on all routes and services, add `aiosqlite`/`aiomysql` drivers, switch to `AsyncSession`/`create_async_engine`, rewrite test fixtures, async-aware `log_io` decorator, update Cookiecutter and demo removal scripts for new structure.
**Source:** Peer review feedback (NEXT_STEPS.md actions 40–47)
**Phase:** 4 (Feedback)

## Epic 26: Code Completeness & Consistency
Small, targeted code fixes that close gaps left by epics 20–25: resolve remaining type suppressions in `main.py`, add coverage exclusion for mock files, remove duplicated `identity_role_mapper` from `entra.py`, refactor auth factory to true dict-dispatch, cache service DI shims with `@lru_cache`, and parenthesize the bare-comma `except` in `logging_decorator.py`.
**Source:** Post-implementation review of FEEDBACK.md residuals
**Phase:** 4 (Feedback)

## Epic 27: Documentation, Naming & Script Alignment
Bring documentation, test file names, and scaffolding scripts into alignment with the post-epic-25 codebase: fix stale references and internal contradictions in `PROJECT_CONTEXT.md`, rename facade-named test files, and update scaffolding scripts to emit current patterns (`CamelCaseModel`, no `from __future__`).
**Source:** Post-implementation review of FEEDBACK.md residuals
**Depends on:** Epic 26
**Phase:** 4 (Feedback)
