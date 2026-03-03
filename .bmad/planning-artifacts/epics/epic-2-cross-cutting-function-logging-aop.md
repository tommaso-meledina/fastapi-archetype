# Epic 2: Cross-Cutting Function Logging (AOP)

A developer can see that all service-layer functions are automatically logged (inputs and return values) via a decorator mechanism applied at the package level — no per-function modification needed.

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
