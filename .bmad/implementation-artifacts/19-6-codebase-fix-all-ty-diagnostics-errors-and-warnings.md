# Story 19.6: Codebase — Fix All ty Diagnostics (Errors and Warnings)

Status: done

## Story

As a **software engineer**,
I want **all ty diagnostics (errors and warnings) resolved so that `uv run ty check` passes with zero output**,
so that **type safety is enforced and the codebase is clean for future changes**.

## Acceptance Criteria

1. **Given** I run `uv run ty check` **When** the command completes **Then** it exits with code 0 **And** it produces no error or warning diagnostics.
2. **Given** the codebase **When** I look for type-check suppressions **Then** there are no broad or unjustified suppressions; any `ty: ignore` or rule downgrades in config are minimal, justified, and documented (e.g. in comments or PROJECT_CONTEXT).
3. **Given** the full quality gate **When** I run ruff check, ruff format --check, ty check, and pytest **Then** all pass.

## Tasks / Subtasks

- [x] Task 1 — Fix src and tests so ty check passes with zero diagnostics.
- [x] Task 2 — Ensure suppressions are minimal and justified (comments where used).
- [x] Task 3 — Run full quality gate (ruff, ty, pytest); all pass.

## Dev Agent Record

### File List

- src/fastapi_archetype/aop/logging_decorator.py (modified)
- src/fastapi_archetype/main.py (modified)
- src/fastapi_archetype/observability/logging.py (modified)
- tests/aop/test_logging_decorator.py (modified)
- tests/auth/test_entra_integration.py (modified)
- tests/auth/test_external_provider.py (modified)
- tests/auth/test_role_mapping.py (modified)
- tests/core/test_errors.py (modified)
- tests/observability/test_logging.py (modified)
