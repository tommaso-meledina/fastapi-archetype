# Changelog


## 1.0.0


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


