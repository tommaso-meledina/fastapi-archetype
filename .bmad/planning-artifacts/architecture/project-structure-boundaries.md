# Project Structure & Boundaries

## Complete Project Directory Structure

```
fastapi-archetype/
├── pyproject.toml                          # Project config, dependencies, Ruff + pytest settings
├── uv.lock                                 # Reproducible dependency lockfile
├── .python-version                         # Python version pin (3.14)
├── .env                                    # Environment variables (not committed)
├── .env.example                            # Template for required env vars
├── .gitignore
├── Dockerfile                              # Multi-stage build (FR24–FR25)
├── README.md
├── src/
│   └── fastapi_archetype/
│       ├── __init__.py
│       ├── main.py                         # App factory, startup sequence, middleware, route inclusion
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py                   # pydantic-settings BaseSettings (FR8–FR9)
│       │   ├── constants.py                # Centralized constants, resource definitions (FR26, FR28)
│       │   ├── errors.py                   # ErrorCode enum, AppException, exception handler (FR3, FR27)
│       │   └── database.py                 # Engine creation, session generator, get_session (FR5)
│       ├── models/
│       │   ├── __init__.py
│       │   └── dummy.py                    # Dummy SQLModel: ORM + Pydantic validation (FR6–FR7)
│       ├── api/
│       │   ├── __init__.py
│       │   └── dummy_routes.py             # GET /dummies, POST /dummies (FR1–FR2, FR4)
│       ├── services/
│       │   ├── __init__.py
│       │   └── dummy_service.py            # Business logic; AOP-decorated target (FR17–FR19)
│       ├── aop/
│       │   ├── __init__.py
│       │   └── logging_decorator.py        # Decorator for function I/O logging (FR17–FR19)
│       └── observability/
│           ├── __init__.py
│           ├── otel.py                     # OpenTelemetry trace setup and configuration (FR20–FR21)
│           └── prometheus.py               # prometheus-fastapi-instrumentator setup (FR22–FR23)
└── tests/
    ├── __init__.py
    ├── conftest.py                         # SQLite engine, session override, TestClient factory
    ├── core/
    │   ├── __init__.py
    │   ├── test_config.py                  # Config validation tests (FR9)
    │   └── test_errors.py                  # Error registry and handler tests (FR3)
    ├── api/
    │   ├── __init__.py
    │   └── test_dummy_routes.py            # Endpoint integration tests (FR13–FR15)
    ├── services/
    │   ├── __init__.py
    │   └── test_dummy_service.py           # Unit tests with mocked dependencies (FR13)
    └── aop/
        ├── __init__.py
        └── test_logging_decorator.py       # AOP decorator behavior tests (FR17)
```

## Architectural Boundaries

**API Boundary (external → application):**
- All external traffic enters through `api/` route modules
- Routes delegate to `services/` — no business logic in route handlers
- Routes receive validated Pydantic/SQLModel objects from FastAPI
- Routes return SQLModel objects; FastAPI handles serialization with camelCase aliases

**Service Boundary (application logic):**
- `services/` contains all business logic
- Services receive a database session via function parameters (passed from route's `Depends()`)
- Services are the AOP-decorated layer — all function I/O logging targets this package
- Services never import from `api/` — dependency flows inward only

**Data Boundary (application → database):**
- `core/database.py` owns engine creation and session lifecycle
- `models/` defines SQLModel classes — the single source of truth for both ORM mapping and API schema
- No raw SQL anywhere; all data access through SQLModel queries
- Database dialect abstraction handled by SQLAlchemy engine configuration, not application code

**Cross-Cutting Boundary (middleware layer):**
- `observability/otel.py` and `observability/prometheus.py` hook into the ASGI middleware stack in `main.py`
- `aop/logging_decorator.py` is applied to `services/` functions
- `core/errors.py` registers a global exception handler in `main.py`
- These modules configure themselves but never contain business logic

## Data Flow

```
Request → FastAPI (validation) → api/routes → services/ (AOP-logged) → SQLModel → Database
                                                                              ↓
Response ← FastAPI (camelCase serialization) ← api/routes ← services/ ← SQLModel ← Database

Cross-cutting (parallel to request flow):
  OTEL middleware → trace span per request
  Prometheus middleware → metrics per request
  AOP decorator → DEBUG log per service function call
  Exception handler → consistent error response on failure
```

## Requirements to Structure Mapping

| Requirement | Primary File(s) | Supporting File(s) |
|---|---|---|
| FR1 (GET /dummies) | `api/dummy_routes.py` | `services/dummy_service.py`, `models/dummy.py` |
| FR2 (POST /dummies) | `api/dummy_routes.py` | `services/dummy_service.py`, `models/dummy.py` |
| FR3 (Structured errors) | `core/errors.py` | `main.py` (handler registration) |
| FR5 (MariaDB connection) | `core/database.py` | `core/config.py` (connection string) |
| FR6–FR7 (Dummy model) | `models/dummy.py` | — |
| FR8–FR9 (Config management) | `core/config.py` | `.env`, `.env.example` |
| FR10–FR12 (API docs) | `main.py` | Implicit via FastAPI |
| FR13–FR16 (Testing) | `tests/conftest.py` | All `test_*.py` files |
| FR17–FR19 (AOP logging) | `aop/logging_decorator.py` | `services/dummy_service.py` (target) |
| FR20–FR21 (OTEL) | `observability/otel.py` | `main.py` (middleware registration) |
| FR22–FR23 (Prometheus) | `observability/prometheus.py` | `main.py` (middleware registration) |
| FR24–FR25 (Docker) | `Dockerfile` | `.env.example` |
| FR26–FR28 (Constants/codes) | `core/constants.py`, `core/errors.py` | — |
