# Story 7.1: Custom Business Counter Metric

Status: done

## Story

As a **software engineer**,
I want **a custom Prometheus counter that tracks a business event (e.g., dummies created) alongside the auto-instrumented HTTP metrics**,
so that **I have a concrete, replicable pattern for adding application-specific metrics to any service built from this archetype**.

## Acceptance Criteria

1. **Given** the application is running **When** I access `/metrics` **Then** the response includes at least one custom application-defined metric (e.g., a counter for dummy creation events) in addition to the auto-instrumented HTTP request metrics.

2. **Given** the application is running **When** I send one or more `POST /dummies` requests with valid payloads **Then** the custom counter metric increments accordingly **And** the updated count is visible at `/metrics`.

3. **Given** the custom metric implementation **When** I inspect the code **Then** the metric is defined using the Prometheus client library directly (not via `prometheus-fastapi-instrumentator` internals) **And** the metric registration and increment pattern is clear enough to serve as a copy-and-adapt example for new domain-specific metrics.

4. **Given** the custom metric **When** I inspect its Prometheus metadata **Then** it has a descriptive name and help string following Prometheus naming conventions.

## Tasks / Subtasks

- [x] Task 1: Define custom Prometheus counter in `observability/prometheus.py` (AC: 1, 3, 4)
  - [x] Import `Counter` from `prometheus_client`
  - [x] Create module-level counter: `DUMMIES_CREATED_TOTAL = Counter("dummies_created_total", "Total number of dummy resources created")` following Prometheus naming conventions (`<noun>_<unit>_total` for counters)
  - [x] Export the counter for use by the service layer
- [x] Task 2: Increment counter in `services/dummy_service.py` on successful creation (AC: 2)
  - [x] Import `DUMMIES_CREATED_TOTAL` from `observability.prometheus`
  - [x] Call `DUMMIES_CREATED_TOTAL.inc()` after successful `session.commit()` in `create_dummy()`
- [x] Task 3: Write tests for the custom metric (AC: 1, 2, 3, 4)
  - [x] Unit test: verify `DUMMIES_CREATED_TOTAL` counter increments when `create_dummy` is called
  - [x] Integration test: verify `/metrics` response includes `dummies_created_total` metric name
  - [x] Integration test: verify counter value increases after POST `/dummies` requests
  - [x] Verify metric has descriptive help string in `/metrics` output
- [x] Task 4: Run quality checks — ruff lint + format, full test suite (AC: all)

## Dev Notes

### Technical Constraints

- **Library**: Use `prometheus_client.Counter` directly — NOT `prometheus-fastapi-instrumentator` internals. The `prometheus_client` package is already installed as a transitive dependency of `prometheus-fastapi-instrumentator>=7.1.0`, so no new dependency is needed.
- **Metric naming**: Follow Prometheus naming conventions — `dummies_created_total`. Counter names should be `<noun>_<verb>_total` or `<noun>_<unit>_total`. Help string must be descriptive.
- **Registration**: Prometheus client library auto-registers metrics with the default `CollectorRegistry` at module import time. Since `prometheus-fastapi-instrumentator`'s `expose(app)` already exposes the default registry at `/metrics`, the custom counter will appear alongside auto-instrumented metrics with no additional wiring.
- **Counter placement**: Define the counter in `observability/prometheus.py` to keep all Prometheus concerns centralized. Import it in the service layer — this is an acceptable coupling since metrics is a cross-cutting concern.

### Architecture Compliance

- The counter is a cross-cutting observability concern, defined in `observability/prometheus.py` [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- The service layer (`services/dummy_service.py`) imports and increments the counter — this is the recommended pattern for domain-specific metrics
- No new dependencies introduced — `prometheus_client` is already a transitive dependency
- No changes to `AppSettings` or `constants.py` required

### Previous Story Intelligence (Story 3.2)

- Story 3-2 established `setup_prometheus(app)` in `observability/prometheus.py` using `Instrumentator().instrument(app).expose(app)` at module level in `main.py`
- Story 3-2 noted "Do NOT import prometheus_client directly" as an anti-pattern for that story's scope. Epic 7 explicitly overrides this: the custom metric MUST use `prometheus_client` directly
- The `/metrics` endpoint is already created by `expose(app)` — it serves the default `CollectorRegistry` which will automatically include any new metrics registered at module level

### File Modification Plan

- `src/fastapi_archetype/observability/prometheus.py` — add `DUMMIES_CREATED_TOTAL` counter definition
- `src/fastapi_archetype/services/dummy_service.py` — import and increment counter
- `tests/observability/test_prometheus.py` — new test file for custom metric unit and integration tests

### Testing Strategy

- **Unit test**: Import counter, call service function, assert counter `_value.get()` increases (use `prometheus_client.REGISTRY` to inspect)
- **Integration test**: Use `TestClient` to POST dummies, then GET `/metrics` and parse output to verify `dummies_created_total` appears with expected value
- **Important**: Prometheus counters are process-global singletons. Tests must account for counter values being cumulative across test functions within a session. Use relative assertions (delta) rather than absolute values.

### Anti-Patterns to Avoid

- Do NOT create a custom `/metrics` endpoint — `expose(app)` already handles this
- Do NOT use `prometheus-fastapi-instrumentator` APIs for the custom metric — use `prometheus_client` directly
- Do NOT reset the counter between requests — counters are monotonically increasing by design
- Do NOT put metric definitions in the service layer — keep them in `observability/prometheus.py`

### References

- [Source: .bmad/planning-artifacts/epics/epic-7-custom-prometheus-metric.md#Story 7.1]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR23a]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Deferred Decisions]
- [Source: .bmad/implementation-artifacts/3-2-prometheus-metrics-instrumentation.md]
- [PyPI: prometheus_client (transitive via prometheus-fastapi-instrumentator)]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Defined `DUMMIES_CREATED_TOTAL = Counter("dummies_created_total", "Total number of dummy resources created")` in `observability/prometheus.py` using `prometheus_client.Counter` directly
- Imported and incremented the counter in `services/dummy_service.py` `create_dummy()` after successful commit
- No new dependencies — `prometheus_client` is already a transitive dependency of `prometheus-fastapi-instrumentator`
- Counter auto-registers with default `CollectorRegistry`, so it appears at `/metrics` alongside auto-instrumented HTTP metrics with zero additional wiring
- 5 new tests: unit-level counter increment (single + multiple), negative test for counter unchanged on failed creation, integration metric endpoint presence + help string, integration counter value reflection via `/metrics`
- All 46 tests pass (5 new + 41 existing), zero regressions
- Ruff lint and format pass

### Change Log

- 2026-03-04: Implemented custom Prometheus business counter metric (Story 7.1) — `dummies_created_total` counter exposed at `/metrics`

### File List

- src/fastapi_archetype/observability/prometheus.py (modified — added Counter import and DUMMIES_CREATED_TOTAL definition)
- src/fastapi_archetype/services/dummy_service.py (modified — import and increment counter)
- tests/observability/__init__.py (created)
- tests/observability/test_prometheus.py (created — 4 tests for custom metric)
