---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - INITIAL_CONTEXT.md
date: 2026-03-03
author: Tom
---

# Product Brief: fastapi-archetype

## Executive Summary

**fastapi-archetype** is a reference implementation that demonstrates a complete, production-grade Python/FastAPI stack -- the modern equivalent of a mature Java/Spring Boot setup. Its initial purpose is to prove that all key enterprise capabilities (ORM with automatic REST exposure, validation, testing, OpenAPI docs, AOP, observability via OTEL/Prometheus, boilerplate reduction, and containerization) can coexist coherently in a single Python/FastAPI application. Its final objective is to package the proven, feature-complete implementation into a scaffolding project (via Cookiecutter) for mass-generating Python/FastAPI microservices with all these capabilities already wired up. The project uses a minimal `/dummies` CRUD resource backed by MariaDB to keep the domain trivial while the infrastructure and cross-cutting concerns remain the focus. Cookiecutter-based scaffolding is deferred to Phase 3, after all expansion features are integrated.

---

## Core Vision

### Problem Statement

Java/Spring Boot offers a mature, well-integrated ecosystem where ORM, REST exposure, testing, documentation, AOP, and observability are all first-class citizens that work together out of the box. In the Python/FastAPI world, each of these capabilities exists independently, but there is no single, cohesive reference showing them all working together end-to-end. Teams assembling these pieces ad-hoc risk inconsistent setups, missing integrations, and wasted effort rediscovering how to wire everything up.

### Problem Impact

Without a proven reference implementation, every new Python microservice starts from scratch: developers must individually research, select, and integrate libraries for ORM, validation, testing, documentation, AOP, and observability. This leads to inconsistent service architectures, fragile integrations, and significant onboarding overhead -- problems that the Java/Spring Boot ecosystem solved long ago through convention and opinionated defaults.

### Why Existing Solutions Fall Short

Existing FastAPI tutorials and templates typically demonstrate only a subset of these capabilities (e.g., a basic CRUD app with SQLAlchemy, or an observability example in isolation). None provide a unified, production-oriented reference that mirrors the breadth of a Spring Boot setup -- covering ORM + REST + validation + testing + OpenAPI + AOP + OTEL + Prometheus + containerization in a single, runnable project.

### Proposed Solution

Build **fastapi-archetype**: a minimal but complete FastAPI application exposing a `/dummies` REST resource (GET all, POST with validation) backed by a MariaDB database via SQLModel/SQLAlchemy. The application integrates:

- **SQLModel** for ORM and Pydantic-based validation in a single model
- **pytest + FastAPI TestClient** for unit and integration testing, with **SQLite in-memory** for self-contained test execution
- **Automatic OpenAPI/Swagger** via FastAPI's built-in capabilities
- **AOP logging** (via plain Python decorators, or `wrapt` if plain decorators prove insufficient) that intercepts and logs input/output of functions in a designated package
- **OpenTelemetry instrumentation** for traces and log export to OTEL collectors
- **Prometheus metrics** via `prometheus-fastapi-instrumentator` exposing a `/metrics` endpoint
- **uv** for dependency management and reproducible builds
- **Dockerfile** for containerized deployment
- **Configuration management** to load and validate environment variables from `.env` file

External dependencies (MariaDB, OTEL collector, Prometheus) are assumed to be available and will be provided via docker-compose in a later phase.

### Key Differentiators

N/A -- this is an internal reference/scaffolding project, not a commercial product.

## Target Users

### Primary Users

**Software engineers** who need to create a new Python/FastAPI application from scratch. These are generic SWEs -- not necessarily Python specialists or Java migrants -- who need a production-ready starting point that comes with ORM, validation, testing, documentation, AOP, observability, and containerization already wired up. They benefit both from the immediate productivity of spinning up a new microservice quickly and from the architectural consistency that a standardized template enforces across services.

### Secondary Users

**DevOps/platform engineers** who benefit marginally from the standardization that fastapi-archetype brings: predictable Dockerfiles, consistent observability endpoints (`/metrics`, OTEL traces), and uniform project structure across Python microservices.

### User Journey

N/A -- as an internal reference/scaffolding project, a formal user journey is not applicable. The interaction model is straightforward: a developer clones or scaffolds from the archetype, replaces the dummy domain with their actual domain, and has a fully-equipped service running.

## Success Metrics

### Phase Definitions

- **Phase 0 (MVP):** Reference implementation with all capabilities except those explicitly deferred to later phases
- **Phase 1:** Docker-compose environment adding MariaDB, OTEL collector, and Prometheus
- **Phase 2:** Expansion features — external IdP authentication/RBAC, rate limiting, API versioning, custom Prometheus metric example
- **Phase 3:** Cookiecutter scaffolding wrapping the feature-complete implementation into a reusable project template

### Phase 0 (MVP) Success Criteria

The MVP is considered complete when all of the following are true:

1. **All MVP capabilities implemented:** ORM (SQLModel), REST endpoints (`GET /dummies`, `POST /dummies` with validation), testing (pytest + TestClient with SQLite in-memory), automatic OpenAPI/Swagger, AOP logging, OpenTelemetry instrumentation, Prometheus metrics (`/metrics`), uv dependency management, Dockerfile, and configuration management (`.env` loading and validation)
2. **Test coverage > 90%** across the codebase
3. **All tests pass**
4. **App starts and serves requests** successfully
5. **Swagger docs render** at `/docs`
6. **Prometheus metrics are exposed** at `/metrics`
7. **OTEL traces are emitted** (verifiable when a collector is available)
8. **Docker image builds successfully**

### Phase 1 Success Criteria

- Docker-compose environment stands up MariaDB, OTEL collector, and Prometheus alongside the application
- The application connects to MariaDB, exports traces to the OTEL collector, and is scraped by Prometheus -- all within the compose environment

### Phase 2 Success Criteria

- Authentication, rate limiting, and API versioning are integrated into the reference implementation
- Custom Prometheus metric example demonstrates a replicable pattern alongside auto-instrumented metrics
- All existing tests continue to pass; new capabilities have corresponding tests

### Phase 3 Success Criteria

- A new project can be scaffolded from the Cookiecutter template and running in under 5 minutes

### Business Objectives

N/A -- internal reference/scaffolding project.

### Key Performance Indicators

N/A -- success is measured by the quality gates above, not by traditional KPIs.

## MVP Scope

### Core Features (Phase 0)

1. **Python 3.14 runtime**
2. **FastAPI framework** as the web application foundation
3. **SQLModel** for ORM and Pydantic-based validation in a single model definition
4. **REST `/dummies` resource:** `GET /dummies` (return all records) and `POST /dummies` (validate and create) backed by a `DUMMY` table in MariaDB
5. **pytest + FastAPI TestClient** for unit and integration testing, with **SQLite in-memory** for self-contained test execution
6. **Automatic OpenAPI/Swagger** documentation rendered at `/docs`
7. **AOP logging** that intercepts and logs input/output of each function within a designated package
8. **OpenTelemetry instrumentation** for traces and log export to OTEL collectors
9. **Prometheus metrics** exposed at `/metrics` via `prometheus-fastapi-instrumentator`
10. **uv** for dependency management and reproducible builds
11. **Dockerfile** for containerized deployment
12. **Configuration management:** load and validate environment variables from `.env` file

### Out of Scope for MVP

| Capability | Deferred To | Rationale |
|---|---|---|
| Docker-compose environment (MariaDB, OTEL collector, Prometheus) | Phase 1 | Infrastructure concern; MVP assumes external services are available |
| Authentication, rate limiting, API versioning, custom Prometheus metric | Phase 2 | Not needed to demonstrate the core architectural capabilities |
| Cookiecutter scaffolding | Phase 3 | Requires proven, feature-complete reference implementation first |

### MVP Success Criteria

Defined in the Success Metrics section above (Phase 0 Success Criteria).

### Future Vision

- **Phase 1:** Docker-compose environment adding MariaDB, OTEL collector, and Prometheus
- **Phase 2:** Expansion features — external IdP authentication/RBAC, rate limiting, API versioning, custom Prometheus metric example
- **Phase 3:** Cookiecutter scaffolding wrapping the feature-complete implementation into a reusable project template
