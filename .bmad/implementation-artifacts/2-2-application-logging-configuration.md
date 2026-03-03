# Story 2.2: Application Logging Configuration

Status: done

## Story

As a **software engineer**,
I want **the application to configure the Python logging subsystem at startup with output to stdout and a configurable log level**,
so that **all application log output (including AOP decorator logs) is visible when I run the app, and I can control verbosity via an environment variable without code changes**.

## Acceptance Criteria

1. When the application starts with no `LOG_LEVEL` environment variable set, Python's root logger is configured with a handler that writes to stdout at `INFO` level, using a human-readable format that includes timestamp, logger name, level, and message.
2. When `LOG_LEVEL=DEBUG` is set, the root logger level is `DEBUG` and AOP function I/O log entries are visible in stdout.
3. When `LOG_LEVEL=WARNING` is set, only `WARNING` and above appear; `INFO` and `DEBUG` entries are suppressed.
4. `AppSettings` in `core/config.py` has a `log_level` field defaulting to `"INFO"`, validated against standard Python logging level names.
5. `.env.example` documents the `LOG_LEVEL` option.

## Tasks / Subtasks

- [x] Task 1: Add `log_level` setting to `AppSettings` in `core/config.py` (AC: 4)
  - [x] Add `log_level: str = "INFO"` field
  - [x] Validate that the value is a recognized Python logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [x] Task 2: Configure logging subsystem in `main.py` lifespan (AC: 1, 2, 3)
  - [x] Call `logging.basicConfig` after `AppSettings()` is created, before database engine creation
  - [x] Set root logger level from `settings.log_level`
  - [x] Use `sys.stdout` as the stream destination
  - [x] Use a human-readable format: `"%(asctime)s %(name)s %(levelname)s %(message)s"`
- [x] Task 3: Update `.env.example` with `LOG_LEVEL` documentation (AC: 5)
- [x] Task 4: Verify behavior — start app with different LOG_LEVEL values and confirm output
- [x] Task 5: Run quality checks (ruff lint + format)

## Dev Notes

### Technical Constraints

- **stdlib only** — use `logging.basicConfig`, no third-party logging libraries.
- **Log format**: human-readable for now. JSON/structured format is an observability concern and can be addressed in Epic 3.
- **Stream**: `sys.stdout` (not stderr) per architecture doc — container best practice for log routing.
- **Startup order**: logging configuration MUST happen after `AppSettings()` validation (needs `log_level` value) but before any component that logs (database engine creation, etc.). This means it goes right after the settings load in the lifespan.
- **`force=True`**: Pass `force=True` to `logging.basicConfig` so it reconfigures even if the root logger already has handlers (uvicorn may have configured the root logger before the lifespan runs).

### Existing Codebase Context

**`main.py` lifespan** (where logging config will be added):
```python
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    settings = AppSettings()
    engine = get_engine(settings)
    SQLModel.metadata.create_all(engine)
    yield
```

**`core/config.py` `AppSettings`** (where `log_level` will be added):
- Already has `debug: bool = False` — `log_level` is a separate, more granular control
- Uses pydantic-settings with `.env` file loading

### File Structure

Files to modify:
- `src/fastapi_archetype/core/config.py` (add `log_level` field)
- `src/fastapi_archetype/main.py` (add `logging.basicConfig` call in lifespan)
- `.env.example` (document `LOG_LEVEL`)

### Architecture Compliance

- Startup sequence: Config validation → Logging config → DB engine → Middleware → Routes [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- Log destination: stdout [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Logging]
- Log format: human-readable in dev [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Logging]
- FR17a [Source: .bmad/planning-artifacts/prd/functional-requirements.md]

### Previous Story Learnings (Story 2.1)

- AOP decorator logs via `logging.getLogger(__name__)` at DEBUG level — this story makes those logs reachable
- The decorator works correctly; it just needs the logging subsystem configured to surface output

### References

- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR17a]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Process Patterns - Logging]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Startup Sequence]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#API & Communication Patterns]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Added `log_level` field to `AppSettings` with default `"INFO"` and a `field_validator` that normalizes to uppercase and rejects invalid level names
- Added `logging.basicConfig(level=..., format=..., stream=sys.stdout, force=True)` in `main.py` lifespan, immediately after config validation
- `force=True` ensures reconfiguration even when uvicorn has already configured the root logger
- Format includes timestamp, logger name, level, and message: `%(asctime)s %(name)s %(levelname)s %(message)s`
- Updated `.env.example` with documented `LOG_LEVEL` option
- Verified: INFO (default) suppresses DEBUG, DEBUG shows AOP logs, WARNING suppresses INFO+DEBUG
- Verified: lowercase `log_level` values are normalized; invalid values rejected with clear error
- Ruff lint and format pass across entire source tree

### Change Log

- 2026-03-03: Implemented application logging configuration (Story 2.2) — added configurable `LOG_LEVEL` setting and `logging.basicConfig` in lifespan startup

### File List

- src/fastapi_archetype/core/config.py (modified)
- src/fastapi_archetype/main.py (modified)
- .env.example (modified)
