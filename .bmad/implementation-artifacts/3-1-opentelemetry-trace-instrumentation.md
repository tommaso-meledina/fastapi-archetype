# Story 3.1: OpenTelemetry Trace Instrumentation

Status: done

## Story

As a **software engineer**,
I want **OpenTelemetry traces automatically emitted for every incoming HTTP request, with export to an OTEL collector when configured and a dedicated toggle to disable export**,
so that **I get distributed tracing out of the box and can control observability overhead per environment**.

## Acceptance Criteria

1. `observability/otel.py` exists and configures the OpenTelemetry SDK for trace instrumentation of incoming HTTP requests, registering as ASGI middleware in `main.py`.
2. With an OTEL collector endpoint configured and `OTEL_EXPORT_ENABLED=true`, a trace span is created per request and exported to the collector.
3. With `OTEL_EXPORT_ENABLED=false` (the default), the application starts and serves requests normally — no traces are exported regardless of collector configuration.
4. Without an OTEL collector configured, the application starts and serves requests normally without errors.
5. Collector endpoint, `OTEL_EXPORT_ENABLED`, and other OTEL settings are sourced from `AppSettings` in `core/config.py`. `OTEL_EXPORT_ENABLED` defaults to `false`.

## Tasks / Subtasks

- [x] Task 1: Add OTEL settings to `AppSettings` in `core/config.py` (AC: 5)
  - [x] Add `otel_export_enabled: bool = False`
  - [x] Add `otel_exporter_endpoint: str = "http://localhost:4317"` (gRPC default)
  - [x] Add `otel_service_name: str = "fastapi-archetype"` (reuses `app_name` default)
- [x] Task 2: Add OpenTelemetry dependencies to `pyproject.toml` (AC: 1, 2)
  - [x] Add `opentelemetry-api>=1.39.1`
  - [x] Add `opentelemetry-sdk>=1.39.1`
  - [x] Add `opentelemetry-instrumentation-fastapi>=0.60b1`
  - [x] Add `opentelemetry-exporter-otlp>=1.39.1`
  - [x] Run `uv sync` to update lockfile
- [x] Task 3: Implement `observability/otel.py` (AC: 1, 2, 3, 4)
  - [x] Create a `setup_otel(app: FastAPI, settings: AppSettings)` function
  - [x] Configure `TracerProvider` with a `Resource` containing `service.name`
  - [x] When `otel_export_enabled` is `True`: add `BatchSpanProcessor` with `OTLPSpanExporter` targeting the configured endpoint
  - [x] When `otel_export_enabled` is `False`: no exporter/processor added (traces are created but discarded — zero overhead on export path)
  - [x] Call `FastAPIInstrumentor.instrument_app(app)` to register ASGI middleware
  - [x] Exclude `/metrics` from instrumentation (will be added in Story 3.2 — avoid tracing the metrics scrape endpoint)
- [x] Task 4: Register OTEL in `main.py` (AC: 1)
  - [x] Import and call `setup_otel(app, settings)` in the lifespan, after logging config and before route inclusion
  - [x] Pass the `app` instance and `settings` to the setup function
- [x] Task 5: Update `.env.example` with OTEL settings (AC: 5)
  - [x] Document `OTEL_EXPORT_ENABLED`, `OTEL_EXPORTER_ENDPOINT`, `OTEL_SERVICE_NAME`
- [x] Task 6: Run quality checks (ruff lint + format)

## Dev Notes

### Technical Constraints

- **Libraries (MUST use exactly these):**
  - `opentelemetry-api >= 1.39.1` — core tracing API
  - `opentelemetry-sdk >= 1.39.1` — SDK implementation (TracerProvider, Resource, BatchSpanProcessor)
  - `opentelemetry-instrumentation-fastapi >= 0.60b1` — `FastAPIInstrumentor` that adds ASGI middleware automatically
  - `opentelemetry-exporter-otlp >= 1.39.1` — OTLP gRPC exporter (includes both proto-grpc and proto-http)
- **No other observability libraries.** Do not add `opentelemetry-distro` or zero-code instrumentation — this is explicit, programmatic setup.
- **Pattern:** A single `setup_otel(app, settings)` function in `observability/otel.py`. No classes, no global state beyond setting the tracer provider.
- **Startup order in `main.py` lifespan:** Config validation → Logging config → **OTEL setup** → DB engine → Schema creation → yield. OTEL must be configured before any request can be served.
- **`FastAPIInstrumentor.instrument_app(app)`** hooks into the ASGI stack; it is NOT registered via `app.add_middleware()`. Call it after creating the TracerProvider.

### Implementation Pattern for `setup_otel`

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_otel(app: FastAPI, settings: AppSettings) -> None:
    resource = Resource(attributes={"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)

    if settings.otel_export_enabled:
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")
```

### Config Fields to Add to `AppSettings`

```python
otel_export_enabled: bool = False
otel_exporter_endpoint: str = "http://localhost:4317"
otel_service_name: str = "fastapi-archetype"
```

These map to env vars `OTEL_EXPORT_ENABLED`, `OTEL_EXPORTER_ENDPOINT`, `OTEL_SERVICE_NAME` via pydantic-settings automatic env binding.

### `main.py` Lifespan Integration

The `setup_otel` call must receive the `app` reference. Since the lifespan receives `_app: FastAPI`, pass it through:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    logging.basicConfig(...)
    setup_otel(app, settings)       # <-- NEW
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    yield
```

Note: rename `_app` to `app` since it is now used.

### Existing Codebase Context

- `src/fastapi_archetype/observability/__init__.py` already exists (empty) — directory is ready.
- `src/fastapi_archetype/observability/otel.py` does NOT exist yet — create it.
- `main.py` lifespan currently: settings → logging → engine → create_all → yield.
- No middleware is currently registered in the ASGI stack.

### Architecture Compliance

- Cross-cutting boundary: `observability/otel.py` hooks into ASGI middleware stack in `main.py` [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- Startup sequence: Config → Logging → Middleware (OTEL, Prometheus) → Route inclusion [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- FR20: Application emits OpenTelemetry traces for incoming requests [Source: .bmad/planning-artifacts/prd/functional-requirements.md]
- FR21: Application exports traces to OTEL collector when configured [Source: .bmad/planning-artifacts/prd/functional-requirements.md]

### Previous Epic Learnings (Epic 2)

- `force=True` needed for `logging.basicConfig` because uvicorn may pre-configure the root logger — similar care may be needed if OTEL SDK sets up its own logging
- The lifespan is the single place for all startup configuration — follow the same pattern
- Field validators in `AppSettings` should normalize input (e.g., the log_level validator uppercases input)

### Anti-Patterns to Avoid

- Do NOT use `opentelemetry-distro` or `opentelemetry-bootstrap` — this is explicit programmatic setup
- Do NOT create a custom ASGI middleware class — use `FastAPIInstrumentor.instrument_app()`
- Do NOT set OTEL environment variables programmatically (`os.environ`) — use `AppSettings` fields passed to SDK constructors
- Do NOT import from `opentelemetry.exporter.otlp.proto.http` — use `grpc` (gRPC is the standard OTLP transport)
- Do NOT add a `NoOpSpanProcessor` when export is disabled — simply don't add any processor; the TracerProvider will create spans but not export them

### References

- [Source: .bmad/planning-artifacts/epics/epic-3-observability-distributed-tracing-and-metrics.md#Story 3.1]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR20, FR21]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Infrastructure & Deployment]
- [PyPI: opentelemetry-sdk 1.39.1, opentelemetry-instrumentation-fastapi 0.60b1]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `otel_export_enabled`, `otel_exporter_endpoint`, `otel_service_name` fields to `AppSettings`
- Added 4 OpenTelemetry dependencies to pyproject.toml: api, sdk, instrumentation-fastapi, exporter-otlp
- Created `observability/otel.py` with `setup_otel(app, settings)` function
- TracerProvider configured with Resource containing service.name
- When export enabled: BatchSpanProcessor + OTLPSpanExporter (gRPC) configured
- When export disabled: no processor added — zero export overhead
- FastAPIInstrumentor.instrument_app() registers ASGI middleware with `/metrics` excluded
- Integrated setup_otel into main.py lifespan after logging config, before DB engine
- Renamed lifespan param from `_app` to `app` since it is now used
- Updated .env.example with OTEL_EXPORT_ENABLED, OTEL_EXPORTER_ENDPOINT, OTEL_SERVICE_NAME docs
- Ruff lint and format pass across entire source tree
- App loads and starts successfully with default settings (export disabled)

### Change Log

- 2026-03-03: Implemented OpenTelemetry trace instrumentation (Story 3.1) — added OTEL SDK setup with configurable export toggle

### File List

- src/fastapi_archetype/core/config.py (modified)
- src/fastapi_archetype/observability/otel.py (created)
- src/fastapi_archetype/main.py (modified)
- pyproject.toml (modified)
- uv.lock (modified)
- .env.example (modified)
