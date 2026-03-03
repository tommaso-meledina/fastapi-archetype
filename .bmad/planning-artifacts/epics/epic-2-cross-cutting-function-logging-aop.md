# Epic 2: Cross-Cutting Function Logging (AOP)

A developer can see that all service-layer functions are automatically logged (inputs and return values) via a decorator mechanism applied at the package level — no per-function modification needed. The Python logging subsystem is configured at startup so that all log output reaches stdout with a configurable level.

## Story 2.1: AOP Function I/O Logging Decorator

As a **software engineer**,
I want **a decorator-based mechanism that automatically logs function input arguments and return values for all service-layer functions**,
So that **I get cross-cutting debug visibility into business logic without modifying individual functions, and I can see the AOP pattern to apply it to new service modules**.

**Acceptance Criteria:**

**Given** `aop/logging_decorator.py` exists
**When** I inspect its contents
**Then** a decorator function exists that logs function input arguments before execution and return values after execution
**And** logging uses `logging.getLogger(__name__)` at `DEBUG` level
**And** the decorator is implemented using plain Python decorators

**Given** `aop/logging_decorator.py` provides an `apply_logging(module)` function
**When** it is called with a module reference
**Then** all public functions in that module are wrapped with the logging decorator without modifying each function individually

**Given** the application starts
**When** the `services/` package initializes
**Then** `apply_logging` is applied to the services module(s), enabling automatic function I/O logging for all service functions

**Given** a service function is called during request processing
**When** the function executes with DEBUG logging enabled
**Then** the input arguments are logged before execution
**And** the return value is logged after execution
**And** log entries are traceable to the source module via `__name__`

**Given** the application runs in production with logging level above DEBUG
**When** service functions execute
**Then** no AOP log output is produced, avoiding noise in production logs

## Story 2.2: Application Logging Configuration

As a **software engineer**,
I want **the application to configure the Python logging subsystem at startup with output to stdout and a configurable log level**,
So that **all application log output (including AOP decorator logs) is visible when I run the app, and I can control verbosity via an environment variable without code changes**.

**Acceptance Criteria:**

**Given** the application starts with no `LOG_LEVEL` environment variable set
**When** the logging subsystem initializes
**Then** Python's root logger is configured with a handler that writes to stdout at `INFO` level
**And** a human-readable format is used including timestamp, logger name, level, and message

**Given** the `LOG_LEVEL` environment variable is set to `DEBUG`
**When** the application starts
**Then** the root logger level is set to `DEBUG`
**And** AOP function I/O log entries are visible in stdout

**Given** the `LOG_LEVEL` environment variable is set to `WARNING`
**When** the application starts
**Then** only `WARNING` and above log entries appear in stdout
**And** `INFO`-level request lifecycle logs and `DEBUG`-level AOP logs are suppressed

**Given** `core/config.py` is inspected
**When** the `AppSettings` class is reviewed
**Then** a `log_level` field exists with a default value of `"INFO"` and validation against standard Python logging level names

**Given** `.env.example` is inspected
**When** its contents are reviewed
**Then** a `LOG_LEVEL` entry documents the available options
