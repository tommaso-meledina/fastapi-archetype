# Epic List

## Epic 1: Running Application with CRUD API
A developer can clone the project, run it immediately (SQLite in-memory by default), and interact with a fully working REST API — with structured error responses, centralized constants, auto-generated API docs at `/docs`, and a clear project structure that serves as a copy-and-adapt template. MariaDB is supported via a configuration toggle.
**FRs covered:** FR1–FR12, FR5a, FR26–FR28
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
