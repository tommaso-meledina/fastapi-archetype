# Story 3.2: Prometheus Metrics Instrumentation

Status: done

## Story

As a **software engineer**,
I want **Prometheus metrics automatically collected for every HTTP request and exposed at `/metrics`**,
so that **I get request count, latency, and status code metrics ready for Prometheus scraping without any per-endpoint instrumentation**.

## Acceptance Criteria

1. `observability/prometheus.py` exists and configures `prometheus-fastapi-instrumentator` for automatic HTTP request metrics, registering as middleware in `main.py`.
2. When the application is running and requests are sent to any endpoint, accessing `/metrics` returns Prometheus-formatted metrics including HTTP request count, latency, and status code breakdowns.
3. The `/metrics` response content type is appropriate for Prometheus scraping (`text/plain` with version parameter or `text/plain`).
4. When a new route is added to the application, metrics are automatically collected without additional configuration.

## Tasks / Subtasks

- [x] Task 1: Add `prometheus-fastapi-instrumentator` dependency to `pyproject.toml` (AC: 1)
  - [x] Add `prometheus-fastapi-instrumentator>=7.1.0`
  - [x] Run `uv sync` to update lockfile
- [x] Task 2: Implement `observability/prometheus.py` (AC: 1, 4)
  - [x] Create a `setup_prometheus(app: FastAPI)` function
  - [x] Use `Instrumentator().instrument(app).expose(app)` pattern
  - [x] The `expose(app)` call registers the `/metrics` endpoint on the app
- [x] Task 3: Register Prometheus in `main.py` (AC: 1)
  - [x] Call `setup_prometheus(app)` at module level after app creation (not in lifespan — `add_middleware` cannot be called after app starts)
- [x] Task 4: Run quality checks (ruff lint + format)

## Dev Notes

### Technical Constraints

- **Library (MUST use exactly):** `prometheus-fastapi-instrumentator >= 7.1.0` — auto-instruments all HTTP requests with zero per-endpoint configuration.
- **Pattern:** A single `setup_prometheus(app: FastAPI)` function in `observability/prometheus.py`. The library handles everything: middleware registration, metrics collection, and `/metrics` endpoint creation.
- **Startup order in `main.py` lifespan:** Config → Logging → OTEL setup → **Prometheus setup** → DB engine → Schema creation → yield. Prometheus middleware must wrap routes to capture metrics.
- **`expose(app)`** creates a GET `/metrics` endpoint automatically — do NOT manually create a route for `/metrics`.
- **No settings needed** — `prometheus-fastapi-instrumentator` works out of the box. No config fields to add to `AppSettings`.

### Implementation Pattern for `setup_prometheus`

```python
from prometheus_fastapi_instrumentator import Instrumentator

def setup_prometheus(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app)
```

This is deliberately minimal. The library automatically:
- Adds ASGI middleware to instrument all requests
- Creates a `/metrics` GET endpoint
- Collects: `http_requests_total`, `http_request_duration_seconds`, `http_request_size_bytes`, `http_response_size_bytes`

### `main.py` Lifespan Integration

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    logging.basicConfig(...)
    tracer_provider = setup_otel(app, settings)
    setup_prometheus(app)                         # <-- NEW
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    yield
    tracer_provider.shutdown()
```

### Existing Codebase Context (after Story 3.1)

- `src/fastapi_archetype/observability/__init__.py` exists (empty)
- `src/fastapi_archetype/observability/otel.py` exists (OTEL setup)
- `main.py` lifespan: settings → logging → OTEL → engine → create_all → yield → tracer_provider.shutdown()
- OTEL's `FastAPIInstrumentor` already excludes `/metrics` from tracing — Prometheus scrapes won't generate trace noise

### Architecture Compliance

- Cross-cutting boundary: `observability/prometheus.py` hooks into middleware stack in `main.py` [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- Startup sequence: Config → Logging → Middleware (OTEL, Prometheus) → Route inclusion [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- FR22: Application exposes Prometheus metrics at `/metrics` [Source: .bmad/planning-artifacts/prd/functional-requirements.md]
- FR23: Application automatically instruments HTTP request metrics [Source: .bmad/planning-artifacts/prd/functional-requirements.md]

### Previous Story Learnings (Story 3.1)

- `setup_otel` returns `TracerProvider` for explicit shutdown — `setup_prometheus` doesn't need this (no cleanup required)
- Lifespan param renamed from `_app` to `app` — already done
- OTEL already excludes `/metrics` from tracing via `excluded_urls="metrics"` — validates that both observability systems work together cleanly

### Anti-Patterns to Avoid

- Do NOT manually create a `/metrics` route — `expose(app)` does this
- Do NOT import `prometheus_client` directly — use `prometheus-fastapi-instrumentator` which wraps it
- Do NOT add custom metrics in this story — only auto-instrumented HTTP metrics
- Do NOT add config fields to `AppSettings` — the library needs no configuration for default behavior

### References

- [Source: .bmad/planning-artifacts/epics/epic-3-observability-distributed-tracing-and-metrics.md#Story 3.2]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR22, FR23]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- [PyPI: prometheus-fastapi-instrumentator 7.1.0]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `prometheus-fastapi-instrumentator>=7.1.0` to pyproject.toml
- Created `observability/prometheus.py` with `setup_prometheus(app)` using `Instrumentator().instrument(app).expose(app)`
- Called `setup_prometheus(app)` at module level in `main.py` (after app creation, router inclusion) — NOT in lifespan because `Instrumentator.instrument()` calls `app.add_middleware()` which raises `RuntimeError` after app startup
- Verified `/metrics` returns 200 with `text/plain; version=1.0.0; charset=utf-8` content type
- Verified metrics include `http_requests_total` (count by handler/method/status), `http_request_duration_seconds` (histogram), `http_request_size_bytes`, `http_response_size_bytes`
- Verified new routes are automatically instrumented
- Ruff lint and format pass across entire source tree

### Change Log

- 2026-03-03: Implemented Prometheus metrics instrumentation (Story 3.2) — auto-instrumented HTTP metrics exposed at /metrics

### File List

- src/fastapi_archetype/observability/prometheus.py (created)
- src/fastapi_archetype/main.py (modified)
- pyproject.toml (modified)
- uv.lock (modified)
