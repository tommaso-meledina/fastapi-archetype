# Epic 7: Custom Prometheus Metric Example

A developer can see a custom application-specific Prometheus metric (a business counter) exposed alongside the auto-instrumented HTTP metrics at `/metrics`, serving as a replicable pattern for adding domain-specific metrics to any service scaffolded from this archetype.

## Story 7.1: Custom Business Counter Metric

As a **software engineer**,
I want **a custom Prometheus counter that tracks a business event (e.g., dummies created) alongside the auto-instrumented HTTP metrics**,
So that **I have a concrete, replicable pattern for adding application-specific metrics to any service built from this archetype**.

**Acceptance Criteria:**

**Given** the application is running
**When** I access `/metrics`
**Then** the response includes at least one custom application-defined metric (e.g., a counter for dummy creation events) in addition to the auto-instrumented HTTP request metrics

**Given** the application is running
**When** I send one or more `POST /dummies` requests with valid payloads
**Then** the custom counter metric increments accordingly
**And** the updated count is visible at `/metrics`

**Given** the custom metric implementation
**When** I inspect the code
**Then** the metric is defined using the Prometheus client library directly (not via `prometheus-fastapi-instrumentator` internals)
**And** the metric registration and increment pattern is clear enough to serve as a copy-and-adapt example for new domain-specific metrics

**Given** the custom metric
**When** I inspect its Prometheus metadata
**Then** it has a descriptive name and help string following Prometheus naming conventions
