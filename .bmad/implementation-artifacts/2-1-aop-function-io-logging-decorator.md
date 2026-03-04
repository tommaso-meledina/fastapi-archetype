# Story 2.1: AOP Function I/O Logging Decorator

Status: done

## Story

As a **software engineer**,
I want **a module-level AOP mechanism that automatically logs function input arguments, return values, and exceptions for all service-layer functions — applied programmatically at package initialization without annotating individual functions**,
so that **I get cross-cutting debug and error visibility into business logic without modifying individual functions, and I can see the AOP pattern to apply it to new service modules**.

## Acceptance Criteria

1. `aop/logging_decorator.py` exists and contains a decorator function that logs function input arguments before execution and return values after execution, using `logging.getLogger(__name__)` at `DEBUG` level.
2. `aop/logging_decorator.py` provides an `apply_logging(module)` function that wraps all public functions in the given module with the logging decorator, without modifying each function individually.
3. When the `services/` package initializes, `apply_logging` is applied to the services module(s), enabling automatic function I/O logging for all service functions.
4. When a service function is called with DEBUG logging enabled, input arguments are logged before execution and the return value is logged after execution, with log entries traceable to the source module via `__name__`.
5. When the application runs with logging level above DEBUG, no AOP log output is produced.

## Tasks / Subtasks

- [x] Task 1: Create `aop/logging_decorator.py` with the logging decorator (AC: 1)
  - [x] Implement `log_io` decorator using plain Python decorator pattern (`functools.wraps`)
  - [x] Use `logging.getLogger(__name__)` for logger creation
  - [x] Log input arguments at DEBUG level before function execution
  - [x] Log return value at DEBUG level after function execution
  - [x] Include the decorated function's qualified name in log messages for traceability
- [x] Task 2: Implement `apply_logging(module)` function (AC: 2)
  - [x] Iterate over all public functions in the given module (names not starting with `_`)
  - [x] Wrap each with the `log_io` decorator using `setattr`
  - [x] Skip non-callable attributes and dunder attributes
- [x] Task 3: Apply AOP logging to services package at initialization (AC: 3)
  - [x] In `services/__init__.py`, import and call `apply_logging` on the `dummy_service` module
  - [x] Ensure this runs at import time so decoration is active before any requests
- [x] Task 4: Verify behavior (AC: 4, 5)
  - [x] Run the application with `DEBUG` logging and confirm I/O logging appears for service calls
  - [x] Confirm no AOP output at `INFO` level or above
- [x] Task 5: Run quality checks (ruff lint + format)

## Dev Notes

### Technical Constraints

- **Plain Python decorators only** (FR19). Do NOT use `wrapt` or any external decorator library. Use `functools.wraps` for proper metadata preservation.
- **Logger**: `logging.getLogger(__name__)` per module — this is a project-wide rule. The logger in `logging_decorator.py` will have name `fastapi_archetype.aop.logging_decorator`.
- **Log level**: `DEBUG` only — avoids production noise (see Implementation Patterns doc: AOP function I/O = DEBUG level).
- **No new dependencies** — only Python stdlib (`logging`, `functools`, `inspect`, `types`).

### Existing Codebase Context

**Target module — `services/dummy_service.py`:**
```python
def get_all_dummies(session: Session) -> list[Dummy]:
    return list(session.exec(select(Dummy)).all())

def create_dummy(session: Session, dummy: Dummy) -> Dummy:
    session.add(dummy)
    session.commit()
    session.refresh(dummy)
    return dummy
```

**`aop/__init__.py`**: Currently empty — placeholder package ready for this story.

**`services/__init__.py`**: Currently empty — will need the `apply_logging` call.

### File Structure

Files to create:
- `src/fastapi_archetype/aop/logging_decorator.py`

Files to modify:
- `src/fastapi_archetype/services/__init__.py` (add `apply_logging` call)

Files NOT to touch:
- `services/dummy_service.py` — the whole point of AOP is that individual functions are not modified
- `main.py` — no changes needed; decoration happens at import time via `services/__init__.py`

### Architecture Compliance

- File location: `aop/logging_decorator.py` per project structure doc [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md]
- AOP is a cross-cutting concern — it configures itself but never contains business logic [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Cross-Cutting Boundary]
- Services are the AOP-decorated layer — all function I/O logging targets this package [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md#Service Boundary]
- Naming: `snake_case` for functions/variables, `PascalCase` for classes [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md]

### Previous Epic Learnings

- Epic 1 established the layered package structure with `aop/` as a placeholder
- `services/__init__.py` is empty and ready for the AOP hookup
- The project uses `from __future__ import annotations` and `TYPE_CHECKING` pattern consistently
- Ruff is configured with rules E, W, F, I, N, UP, B, SIM, TCH — code must pass lint

### References

- [Source: .bmad/planning-artifacts/epics/epic-2-cross-cutting-function-logging-aop.md]
- [Source: .bmad/planning-artifacts/prd/functional-requirements.md#FR17-FR19]
- [Source: .bmad/planning-artifacts/architecture/project-structure-boundaries.md]
- [Source: .bmad/planning-artifacts/architecture/implementation-patterns-consistency-rules.md#Process Patterns - Logging]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Package structure]

## Senior Developer Review (AI)

**Review Date:** 2026-03-03
**Review Outcome:** Approve (with 1 auto-fixed issue)

### Findings

**MEDIUM (1 — auto-fixed):**
1. `apply_logging` wrapped all functions in module namespace including imports (e.g. `select` from sqlmodel). Fixed by adding `__module__` check to only wrap functions defined in the target module.

**LOW (2 — noted, not blocking):**
1. No idempotency guard; calling `apply_logging` twice double-wraps functions.
2. `%r` formatting of args may be verbose for complex objects (Session, SQLModel instances).

### Action Items

- [x] Fix `apply_logging` to filter by `attr.__module__ == module.__name__` (MEDIUM — auto-fixed)

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Created `aop/logging_decorator.py` with `log_io` decorator using `functools.wraps` for metadata preservation
- `log_io` logs function qualified name, input args, and return value at DEBUG level via `logging.getLogger(__name__)`
- Implemented `apply_logging(module)` that iterates public functions in a module and wraps them with `log_io` using `setattr`; skips private/dunder names and non-function callables
- Updated `services/__init__.py` to call `apply_logging(dummy_service)` at import time
- Verified both `get_all_dummies` and `create_dummy` are correctly wrapped (`__wrapped__` attribute present, `__name__` preserved)
- Confirmed DEBUG-level log output for function I/O, and no output at INFO level or above
- App loads and serves all routes correctly with AOP applied
- Ruff lint and format checks pass across entire source tree (zero issues)
- Code review fixed: `apply_logging` now filters by `__module__` to avoid wrapping imported functions

### Change Log

- 2026-03-03: Implemented AOP function I/O logging decorator (Story 2.1) — created `logging_decorator.py` with `log_io` and `apply_logging`, hooked into services package initialization
- 2026-03-03: Code review fix — `apply_logging` now only wraps functions defined in the target module (filters by `__module__`)

### File List

- src/fastapi_archetype/aop/logging_decorator.py (created)
- src/fastapi_archetype/services/__init__.py (modified)
