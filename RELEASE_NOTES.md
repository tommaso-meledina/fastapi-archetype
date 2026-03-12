# Changelog


## Upcoming release


### Documentation

* further specify commit syntax in AGENTS.md
* add profile and service contracts pattern and Epic 18
* clarify Docker Compose is for local testing only, not part of product
* add Epic 19 static type checking with ty and sprint plan
* prepare epics after SWE review
* update PROJECT_CONTEXT for epic 21 conventions (story 21.4)


### Fixes

* satisfy ruff E501 and I001 in database and main


### Features

* add PROFILE config and epic 18 sprint plan (story 18-1 done)
* implement profile and service contracts for v1&#x2F;v2 dummies (epic 18 complete)
* add static type checking with Astral ty (epic 19)
* add PYTHONDONTWRITEBYTECODE, PYTHONUNBUFFERED and configurable uvicorn workers to Dockerfile
* add tests&#x2F;auth&#x2F;__init__.py, pytest-asyncio dep, and replace anyio markers
* introduce LogLevel StrEnum for log_level config field and add ipdb dev dep
* remove from __future__ and clean up import hygiene (story 21.1)
* introduce CamelCaseModel base and remove entity alias leakage (story 21.3)
* introduce AppSettings module-level singleton (story 22.1)
* add __all__ to key packages and Justfile task runner (story 22.2)
* migrate logging infrastructure to structlog
* test suite cleanup for epic 23


### Refactoring

* make mock dummy services return static values only (no in-memory store)
* align v1 naming with v2 (DummyServiceV1Contract, get_dummy_service_v1, etc.)
* simplify _default_uuid, add kw_only&#x3D;True to dataclasses, remove slots&#x3D;True from Principal
* replace class hierarchies with plain functions and dict-dispatch (epic 24)



## 0.0.2


### Fixes

* replace bare &#39;archetype&#39; DB username in compose&#x2F;.env
* include uv.lock in generated projects
* enforce single source of truth for database params in compose env file
* remove unnecessary exclusions from project generation logic
* also remove PROJECT_CONTEXT.md exclusion from project generation logic
* address PyCharm inspection results across scripts, src, and tests
* correct database init behaviour


### Features

* add env-configurable CORS support


### Documentation

* add Epic 14 token-only RBAC shard
* add Epic 15 and stories for entity, DTO, and factories separation
* add Epic 16 and align PROJECT_CONTEXT with UUID and PUT-by-UUID
* prepare specs for epic 17


### Refactoring

* remove graph invocation from RBAC flow
* improve sample update-by-UUID pattern



## 0.0.1


### Features

* initialize project with FastAPI skeleton and package structure
* add configuration management with pydantic-settings
* add centralized constants and error handling framework
* add database layer with SQLModel and Dummy entity
* add REST API endpoints and service layer for &#x2F;dummies
* add SQLite in-memory as default database driver
* add AOP function I&#x2F;O logging decorator for service layer
* configure logging subsystem with configurable LOG_LEVEL
* add OpenTelemetry trace instrumentation with configurable export
* add Prometheus metrics instrumentation at &#x2F;metrics endpoint
* add pytest test infrastructure with SQLite in-memory fixtures
* add comprehensive test coverage for all application layers
* add multi-stage Dockerfile for production-ready containerization
* add configurable ROOT_PATH for reverse proxy support
* sketch Docker compose environment
* refine Docker Compose for application and MariaDB (Story 6.1)
* add debug exporter to OTEL collector for trace verification (Story 6.2)
* add GET &#x2F;health endpoint (FR29)
* add custom Prometheus business counter metric (Epic 7)
* add API versioning with &#x2F;v1&#x2F; URL prefix (Epic 8)
* add &#x2F;v2&#x2F;dummies alongside &#x2F;v1&#x2F; to demonstrate version coexistence
* add api_version label to dummies_created_total counter
* add per-endpoint rate limiting with slowapi (Epic 9)
* implement auth&#x2F;authz capabilities
* sanitize auth error responses to prevent leaking provider internals
* add pluggable RoleMappingProvider abstraction for role-to-external-id mapping
* add AOP exception-path logging, revise ADs 09&#x2F;10&#x2F;21, create Epic 12
* decouple auth and observability tests from Dummy endpoints (Epic 13, Story 13.1)
* add demo removal script (Epic 13, Story 13.2)
* add Cookiecutter template build script (Phase 3)
* one-shot project creation with build_template.py


### Documentation

* add initial README with purpose and usage instructions
* add Story 1.6 (configurable DB driver) to specs and tracking
* add FR17a logging subsystem configuration to PRD and architecture
* add FR23a custom Prometheus metric requirement (Phase 3)
* resequence phases — templatize last, expand first
* add Epic 6 (Docker Compose), FR29 (health endpoint), and Story 1.7
* add Phase 2 expansion epics (7–10) with FRs and architecture decisions
* rewrite README with full capability coverage and usage guide
* use neutral tone in README capability descriptions
* add extension guide for adding new resources to the application
* add PROJECT_CONTEXT.md as LLM-oriented project reference
* add ARCH_DECISIONS.md with all 24 architectural decisions
* chisel README file
* add automatic changelog capability to README
* align logging specs and resolve stale requirement references
* add demo removal feature requirements and Epic 13
* add one-liner instructions to README


### Refactoring

* improve AOP log readability with named params and compact repr
* version api and services symmetrically under v1&#x2F; and v2&#x2F;
* wrap custom Prometheus metrics in typed dataclass structure
* replace python-jose with PyJWT for JWT validation


### Fixes

* replace curl health check with python urllib in compose
* use OTEL Collector contrib image and add Prometheus global config
* replace removed jaeger exporter with otlp&#x2F;jaeger in OTEL collector
* code review fixes for rate limiting (Epic 9)
* add missing Epic 10 to sprint status and fix index indentation
* cleanly dispose DB engines and raise test coverage
* decouple test suite from .env file


### Integration

* set up automatic changelog


