# Epic 6: Docker Compose Development Environment

A developer can run `docker compose up` and get the full application running against MariaDB with traces flowing to an OTEL collector and metrics scraped by Prometheus — a complete production-like environment with no manual service setup.

**Implementation note:** The `./compose/` directory already contains a draft Docker Compose setup (with MariaDB, OTEL collector, Prometheus, Jaeger, and Grafana services) along with OTEL collector and Prometheus configuration files. This epic's implementation should adapt and perfect that existing foundation rather than starting from scratch.

## Story 6.1: Docker Compose with Application and MariaDB

As a **software engineer**,
I want **a Docker Compose configuration that starts the application alongside a MariaDB instance with automatic database provisioning**,
So that **I can exercise the full application against a real database with a single command, matching the production database engine**.

**Implementation note:** The existing `./compose/docker-compose.yaml` already defines `mariadb` and `fastapi-archetype` services with health checks, volume mounts, and network configuration. This story should refine and complete that existing setup.

**Acceptance Criteria:**

**Given** the compose file exists in the `./compose/` directory
**When** I inspect its contents
**Then** it defines at least two services: the application and MariaDB
**And** the application service builds from the existing `Dockerfile`
**And** the MariaDB service uses the official `mariadb` image

**Given** the compose environment
**When** I run `docker compose up`
**Then** MariaDB starts and creates the application database automatically via MariaDB's Docker entrypoint environment variables
**And** the application starts after MariaDB is healthy
**And** the application connects to MariaDB using `DB_DRIVER=mysql+pymysql`

**Given** the compose environment is running
**When** I send `POST /dummies` followed by `GET /dummies`
**Then** data is persisted in MariaDB and returned correctly

**Given** the compose environment
**When** I run `docker compose down` followed by `docker compose up`
**Then** MariaDB data persists across restarts via a Docker volume

**Given** the compose environment
**When** I inspect the service configuration
**Then** the application's database connection settings (host, port, user, password, database name) are configured through environment variables or an env file appropriate for the compose network
**And** the MariaDB service has a health check that the application service depends on

## Story 6.2: Observability Stack — OTEL Collector and Prometheus

As a **software engineer**,
I want **an OTEL collector and Prometheus running alongside the application in the compose environment**,
So that **I can verify traces are exported and metrics are scraped end-to-end without setting up external observability infrastructure**.

**Implementation note:** The existing `./compose/docker-compose.yaml` already defines OTEL collector, Prometheus, Jaeger, and Grafana services, and `./compose/observability/` contains draft OTEL collector and Prometheus configuration files. This story should refine and complete that existing setup — including the Jaeger and Grafana services already present.

**Acceptance Criteria:**

**Given** the compose file includes observability services
**When** I inspect its contents
**Then** it defines an OTEL collector service using the official OpenTelemetry Collector image
**And** it defines a Prometheus service using the official `prom/prometheus` image

**Given** an OTEL collector configuration file exists in `./compose/observability/`
**When** I inspect its contents
**Then** it configures an OTLP gRPC receiver matching the application's `OTEL_EXPORTER_ENDPOINT`
**And** it defines at least a logging or debug exporter so traces can be verified

**Given** a Prometheus configuration file exists in `./compose/observability/`
**When** I inspect its contents
**Then** it defines a scrape job targeting the application's `/metrics` endpoint on the compose network

**Given** the compose environment is running
**When** I send requests to the application
**Then** the application has `OTEL_EXPORT_ENABLED=true` and exports traces to the OTEL collector
**And** the OTEL collector receives the traces without errors

**Given** the compose environment is running
**When** I access the Prometheus UI
**Then** the application target appears as UP in the Prometheus targets page
**And** application HTTP metrics (request count, latency) are queryable in Prometheus
