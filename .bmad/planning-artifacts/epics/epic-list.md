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
