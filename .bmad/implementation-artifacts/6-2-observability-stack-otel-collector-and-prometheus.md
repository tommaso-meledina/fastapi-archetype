# Story 6.2: Observability Stack — OTEL Collector and Prometheus

Status: review

## Story

As a **software engineer**,
I want **an OTEL collector and Prometheus running alongside the application in the compose environment**,
so that **I can verify traces are exported and metrics are scraped end-to-end without setting up external observability infrastructure**.

## Acceptance Criteria

1. **Given** the compose file includes observability services **When** I inspect its contents **Then** it defines an OTEL collector service using the official OpenTelemetry Collector image **And** it defines a Prometheus service using the official `prom/prometheus` image.

2. **Given** an OTEL collector configuration file exists in `./compose/observability/` **When** I inspect its contents **Then** it configures an OTLP gRPC receiver matching the application's `OTEL_EXPORTER_ENDPOINT` **And** it defines at least a logging or debug exporter so traces can be verified.

3. **Given** a Prometheus configuration file exists in `./compose/observability/` **When** I inspect its contents **Then** it defines a scrape job targeting the application's `/metrics` endpoint on the compose network.

4. **Given** the compose environment is running **When** I send requests to the application **Then** the application has `OTEL_EXPORT_ENABLED=true` and exports traces to the OTEL collector **And** the OTEL collector receives the traces without errors.

5. **Given** the compose environment is running **When** I access the Prometheus UI **Then** the application target appears as UP in the Prometheus targets page **And** application HTTP metrics (request count, latency) are queryable in Prometheus.

## Tasks / Subtasks

- [x] Task 1: Add debug exporter to OTEL collector configuration (AC: 2)
  - [x] Add `debug` exporter to `compose/observability/otel-collector-config.yaml`
  - [x] Include `debug` exporter in the traces pipeline so trace reception is visible in collector logs
- [x] Task 2: Verify and refine OTEL collector configuration (AC: 2, 4)
  - [x] Confirm OTLP gRPC receiver is configured on port 4317 (matching `OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317`)
  - [x] Confirm traces pipeline: `otlp` receiver → `batch` processor → `jaeger` + `debug` exporters
  - [x] Confirm metrics pipeline: `otlp` receiver → `prometheus` exporter
- [x] Task 3: Verify Prometheus scrape configuration (AC: 3, 5)
  - [x] Confirm `compose/observability/prometheus.yaml` targets `fastapi-archetype:8000` on `/metrics`
  - [x] Confirm scrape interval is reasonable (10s)
- [x] Task 4: Verify application observability environment variables in compose (AC: 4)
  - [x] Confirm `OTEL_EXPORT_ENABLED=true` is set in `compose/.env`
  - [x] Confirm `OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317` uses compose service name
- [x] Task 5: Run quality checks
  - [x] `uv run ruff check src/ tests/` passes
  - [x] `uv run ruff format --check src/ tests/` passes
  - [x] `uv run pytest` — 40 tests pass, no regressions

## Dev Notes

### Architecture Compliance

- OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp` [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md]
- Prometheus: `prometheus-fastapi-instrumentator` auto-instruments HTTP request metrics [Source: same]
- OTEL traces exported via OTLP gRPC when `OTEL_EXPORT_ENABLED=true` [Source: src/fastapi_archetype/observability/otel.py]
- Prometheus metrics exposed at `/metrics` via instrumentator [Source: src/fastapi_archetype/observability/prometheus.py]

### Existing Foundation

**OTEL Collector (`compose/observability/otel-collector-config.yaml`):**
- Receivers: `otlp` with `grpc` and `http` protocols (ports 4317/4318)
- Exporters: `prometheus` (port 8889), `jaeger` (endpoint: `jaeger-all-in-one:14250`)
- Processors: `batch`
- Pipelines: traces → `[otlp] → [batch] → [jaeger]`; metrics → `[otlp] → [prometheus]`
- Missing: `debug` exporter for trace verification (required by AC2)

**Prometheus (`compose/observability/prometheus.yaml`):**
- Scrape job: `fastapi-archetype` targeting `fastapi-archetype:8000` on `/metrics` every 10s
- This is already correctly configured.

**Compose services (from Story 6.1):**
- `otel-collector`: uses `${OTELCOL_IMG}` (default: `otel/opentelemetry-collector:latest`), depends on `jaeger-all-in-one`
- `prometheus`: uses `prom/prometheus:latest`, mounts `prometheus.yaml`
- `jaeger-all-in-one`: uses `jaegertracing/all-in-one:latest`, exposes UI on port 16686
- `grafana`: uses `grafana/grafana-oss`, depends on prometheus

**Application config (`compose/.env`):**
- `OTEL_EXPORT_ENABLED=true` — already set
- `OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317` — already set, uses compose service name

### Key Implementation Details

- The `debug` exporter in the OTEL Collector outputs trace data to the collector's stdout, making it visible in `docker compose logs otel-collector`
- The existing `jaeger` exporter uses the legacy `jaeger` protocol. The `jaegertracing/all-in-one` image supports this protocol on port 14250.
- The `prometheus` exporter in the OTEL Collector exposes _collector-received_ metrics (from app's OTEL SDK). This is separate from the app's own `/metrics` endpoint (which uses `prometheus-fastapi-instrumentator`).
- Prometheus scrapes the app's `/metrics` directly — it does NOT scrape the OTEL collector's Prometheus exporter for HTTP metrics.

### Previous Story Intelligence

- Story 6.1: Created `compose/.env` with all environment variables, refined docker-compose.yaml. Health check fixed to use Python urllib instead of curl. All 40 tests pass.
- Story 3.1: OTEL trace instrumentation — `setup_otel()` configures `TracerProvider` with `OTLPSpanExporter` targeting `otel_exporter_endpoint` via gRPC, `insecure=True`.
- Story 3.2: Prometheus metrics instrumentation — `setup_prometheus()` uses `Instrumentator().instrument(app).expose(app)` exposing `/metrics`.

### References

- [Source: .bmad/planning-artifacts/epics/epic-6-docker-compose-infrastructure.md#Story 6.2]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md]
- [Source: src/fastapi_archetype/observability/otel.py]
- [Source: src/fastapi_archetype/observability/prometheus.py]
- [Source: compose/observability/otel-collector-config.yaml]
- [Source: compose/observability/prometheus.yaml]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `debug` exporter (verbosity: basic) to OTEL collector config and included it in the traces pipeline
- Removed placeholder `const_labels` from Prometheus exporter in OTEL collector config
- Verified OTLP gRPC receiver on default port 4317 matches `OTEL_EXPORTER_ENDPOINT`
- Verified Prometheus scrape config targets `fastapi-archetype:8000` on `/metrics` every 10s
- Verified `OTEL_EXPORT_ENABLED=true` and `OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317` in compose/.env
- All 40 existing tests pass, lint and format checks clean

### Change Log

- 2026-03-04: Implemented Observability Stack — OTEL Collector and Prometheus (Story 6.2)

### File List

- compose/observability/otel-collector-config.yaml (modified — added debug exporter, removed const_labels)
