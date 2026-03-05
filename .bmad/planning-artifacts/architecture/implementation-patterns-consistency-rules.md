# Implementation Patterns & Consistency Rules

## Naming Patterns

**Python Code (PEP 8 compliant):**

| Construct | Convention | Example |
|---|---|---|
| Functions / variables | `snake_case` | `get_all_dummies`, `dummy_service` |
| Classes | `PascalCase` | `Dummy`, `AppException`, `AppSettings` |
| Constants | `UPPER_SNAKE_CASE` | `DUMMIES_PATH`, `DEFAULT_PAGE_SIZE` |
| Enum members | `UPPER_SNAKE_CASE` | `ErrorCode.DUMMY_NOT_FOUND` |
| Modules / files | `snake_case` | `dummy_routes.py`, `error_registry.py` |
| Packages | `snake_case` | `fastapi_archetype`, `api`, `core` |

**Database:**

| Construct | Convention | Example |
|---|---|---|
| Table names | `UPPER_SNAKE_CASE` (explicit `__tablename__`) | `DUMMY` |
| Column names | `snake_case` | `id`, `name`, `created_at` |

**API:**

| Construct | Convention | Example |
|---|---|---|
| Endpoint paths | Lowercase; plural for collections, singular for singletons; verbs forbidden | `/dummies`, `/dummies/{id}` |
| JSON field names | camelCase (via Pydantic `alias_generator`) | `errorCode`, `createdAt` |
| Query parameters | camelCase | `pageSize`, `sortBy` |
| HTTP methods | Standard REST semantics | `GET` = read, `POST` = create |

## Format Patterns

**Success Responses:**
Direct SQLModel/Pydantic serialization — no envelope wrapper. Response body is the model or list of models.

**Error Responses:**
Consistent structure for all application errors:
- `errorCode`: string from `ErrorCode` enum — machine-readable, stable
- `message`: human-readable string paired with the code in the registry
- `detail`: optional additional context; `null` when not applicable

**Date/Time:** ISO 8601 strings in UTC (`2026-03-03T12:00:00Z`)

## Structure Patterns

**Project Organization (src layout per Python Packaging User Guide):**

| Area | Convention | Example |
|---|---|---|
| Source root | `src/` layout | `src/fastapi_archetype/` |
| Entry point | `main.py` at package root | `src/fastapi_archetype/main.py` |
| Configuration | `pyproject.toml` as single project config | Tool settings (Ruff, pytest) in `pyproject.toml` |
| Layer modules | One module per layer initially; promote to package when multiple files needed | `routes.py` → `routes/dummies.py` when second resource added |
| Configuration module | Single `config.py` in `core/` | `src/fastapi_archetype/core/config.py` |
| Constants | Single `constants.py` in `core/` | `src/fastapi_archetype/core/constants.py` |
| Error registry | Single `errors.py` in `core/` | `src/fastapi_archetype/core/errors.py` |

**Test Organization:**

| Area | Convention | Example |
|---|---|---|
| Test location | `tests/` at project root, mirroring source structure | `tests/api/test_dummy_routes.py` |
| Test file naming | `test_` prefix | `test_dummy_routes.py` |
| Test function naming | `test_` prefix, descriptive of behavior | `test_create_dummy_returns_201` |
| Shared fixtures | `conftest.py` at `tests/` root | Session override, test client factory |

## Process Patterns

**Logging (Python logging best practices):**

| Area | Convention | Rationale |
|---|---|---|
| Logging configuration | Standards-first stdlib logging configuration in `main.py` lifespan; level from `LOG_LEVEL`, mode from `LOG_MODE` (`plain` default, `json` optional) | Single configuration point at startup; environment-driven behavior; safe fallback to `plain` on invalid mode |
| Logger creation | `logging.getLogger(__name__)` per module | Python standard; enables per-module log control; traceable to source |
| Log destination | stdout, unbuffered | Container best practice; OTEL collector and Docker handle routing |
| AOP function I/O | `DEBUG` level (inputs/outputs), `ERROR` level (exceptions) | I/O avoids noise in production; exceptions always surface |
| Request lifecycle | `INFO` level | Normal operational visibility |
| Recoverable issues | `WARNING` level | Attention-worthy but not failures |
| Failures | `ERROR` level | Requires investigation |
| Log format | `plain`: UTC ISO-8601 + `traceId` + level + message; `json`: one JSON object per line with camelCase fields (`timestamp`, `level`, `logger`, `message`, `traceId`), `NO_TRACE_ID` fallback | Supports both human troubleshooting and machine parsing with consistent correlation semantics |

**Validation:**

| Area | Convention | Rationale |
|---|---|---|
| Validation timing | At API boundary only (Pydantic/SQLModel on request entry) | Single validation point; no redundant checks deeper in the stack |

**Startup Sequence:**

| Order | Step | Rationale |
|---|---|---|
| 1 | Configuration validation (pydantic-settings) | Fail-fast: config errors surface before any I/O |
| 1a | Logging subsystem configuration | Depends on validated config (`LOG_LEVEL`, `LOG_MODE`); must be active before any component logs |
| 2 | Database engine creation | Depends on validated config |
| 3 | Middleware registration (OTEL, Prometheus) | Depends on config; must wrap routes |
| 4 | Route inclusion | Last; all infrastructure ready |

**Import Ordering:**
Enforced by Ruff (isort-compatible rules). No manual decision needed.

## Enforcement Guidelines

**All AI agents implementing this project MUST:**
- Follow PEP 8 naming conventions for all Python code
- Use camelCase for all JSON field names via Pydantic alias generation — never manual aliasing
- Use `logging.getLogger(__name__)` for all loggers — never `print()` or shared logger instances
- Place all error codes in `core/errors.py` — never define error codes inline in route handlers
- Place all constants in `core/constants.py` — never scatter string literals through the codebase
- Use FastAPI `Depends()` for all database session access — never create sessions manually in routes
- Write tests in `tests/` mirroring the source structure — never co-locate tests with source
