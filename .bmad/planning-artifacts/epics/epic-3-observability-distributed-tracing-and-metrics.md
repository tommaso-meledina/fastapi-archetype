# Epic 3: Observability — Distributed Tracing and Metrics

A developer can see OpenTelemetry traces emitted for every request and Prometheus metrics exposed at `/metrics` — full observability with zero additional setup.

## Story 3.1: OpenTelemetry Trace Instrumentation

As a **software engineer**,
I want **OpenTelemetry traces automatically emitted for every incoming HTTP request, with export to an OTEL collector when configured and a dedicated toggle to disable export**,
So that **I get distributed tracing out of the box and can control observability overhead per environment**.

**Acceptance Criteria:**

**Given** `observability/otel.py` exists
**When** I inspect its contents
**Then** it configures the OpenTelemetry SDK for trace instrumentation of incoming HTTP requests
**And** it registers as ASGI middleware in `main.py`

**Given** the application is running with an OTEL collector endpoint configured and `OTEL_EXPORT_ENABLED=true`
**When** an HTTP request is processed
**Then** a trace span is created for the request
**And** the trace is exported to the configured OTEL collector

**Given** the application is running with `OTEL_EXPORT_ENABLED=false`
**When** an HTTP request is processed
**Then** the application starts and serves requests normally without errors
**And** no traces are exported regardless of collector configuration

**Given** the application is running without an OTEL collector configured
**When** an HTTP request is processed
**Then** the application starts and serves requests normally without errors

**Given** the OTEL configuration
**When** I inspect how it reads settings
**Then** collector endpoint, `OTEL_EXPORT_ENABLED`, and other OTEL settings are sourced from `AppSettings` configuration
**And** `OTEL_EXPORT_ENABLED` defaults to `false`

## Story 3.2: Prometheus Metrics Instrumentation

As a **software engineer**,
I want **Prometheus metrics automatically collected for every HTTP request and exposed at `/metrics`**,
So that **I get request count, latency, and status code metrics ready for Prometheus scraping without any per-endpoint instrumentation**.

**Acceptance Criteria:**

**Given** `observability/prometheus.py` exists
**When** I inspect its contents
**Then** it configures `prometheus-fastapi-instrumentator` for automatic HTTP request metrics
**And** it registers as middleware in `main.py`

**Given** the application is running
**When** I send requests to any endpoint and then access `/metrics`
**Then** the response contains Prometheus-formatted metrics
**And** metrics include HTTP request count, latency, and status code breakdowns

**Given** the application is running
**When** I access `/metrics`
**Then** the response content type is appropriate for Prometheus scraping

**Given** the instrumentation setup
**When** a new route is added to the application
**Then** metrics are automatically collected for the new route without additional configuration
