# Epic 26: Code Completeness & Consistency

Small, targeted code fixes that close gaps left by epics 20–25: residual type suppressions, missing coverage exclusions, duplicated definitions, an if/else that should be dict-dispatch, uncached DI shims, and a bare-comma `except`.

> **Source:** Post-implementation review of FEEDBACK.md residuals ([NEW_REQUIREMENTS.md](../../../NEW_REQUIREMENTS.md)).
> **Phase:** 4 (Feedback)

## Context

After epics 20–25 were implemented, a review of the codebase against the original feedback surfaced six code-level issues: one remaining `type: ignore`, missing coverage exclusion for mock files, a duplicated function definition, an if/else factory that should be dict-dispatch, uncached service DI shims, and a bare-comma `except` form. None are architectural; all are completion-quality items.

## Problem Statement

- A `# type: ignore[union-attr]` remains in `main.py` (line 42) and a `# ty: ignore[invalid-argument-type]` on the `CORSMiddleware` call (line 73), despite Epic 21 targeting zero suppressions.
- Mock implementation files are not excluded from coverage measurement.
- `identity_role_mapper` is defined both in `auth/role_mapping.py` (canonical) and locally in `auth/entra.py` (line 176).
- `auth/factory.py` docstring says "dict-dispatch" but the implementation is if/else with a lazy try/except — inconsistent with the service factory which uses genuine dict-dispatch.
- Service DI shims (`get_dummy_service_v1`, `get_dummy_service_v2`) rebuild the service dataclass on every call, while `get_auth_functions` uses `@lru_cache`.
- `except ValueError, TypeError:` in `logging_decorator.py` (line 34) uses the bare-comma form; every other multi-type `except` in the codebase uses parentheses.

## Proposed Epic Goal

Resolve all six issues with minimal, targeted changes. No architecture changes; no new dependencies.

## Success Criteria

- Zero `# type: ignore` comments in `src/`.
- Any remaining `# ty: ignore` has a brief inline comment explaining the library typing limitation.
- `pyproject.toml` coverage config excludes mock implementation files.
- `identity_role_mapper` is defined only in `auth/role_mapping.py`; `entra.py` imports it.
- `get_auth()` uses a dict mapping from `auth_type` to a builder callable (true dict-dispatch).
- Both service DI shims are decorated with `@lru_cache`.
- All `except` clauses with multiple types use the parenthesized tuple form.
- All quality checks pass.

## Stories

### Story 26.1: Replace Remaining Type Suppressions in `main.py`

As a **developer**,
I want **the `type: ignore` and unjustified `ty: ignore` comments removed from `main.py`**,
so that **the codebase has zero unexplained type suppressions**.

**Acceptance Criteria:**

- **Given** `src/` **When** I search for `# type: ignore` **Then** zero matches are found.
- **Given** `main.py` line 42 (`Dummy.__table__.update()`) **When** I inspect it **Then** the union ambiguity is resolved via `cast()` or query restructuring.
- **Given** `main.py` line 73 (`CORSMiddleware`) **When** I inspect it **Then** the type mismatch is resolved, or the `# ty: ignore` remains with a brief inline comment explaining the library typing limitation.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 26.2: Add Coverage Exclusion for Mock Implementation Files

As a **developer**,
I want **mock implementation files excluded from coverage measurement**,
so that **coverage reports reflect only production code**.

**Acceptance Criteria:**

- **Given** `pyproject.toml` `[tool.coverage.run]` or `[tool.coverage.report]` **When** I inspect it **Then** an `omit` pattern excludes mock service modules (e.g. `**/mock_dummy.py`).
- **Given** the test suite **When** I run `uv run pytest --cov` **Then** mock modules do not appear in coverage output.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 26.3: Remove Duplicated `identity_role_mapper` from `entra.py`

As a **developer**,
I want **`identity_role_mapper` defined only in `auth/role_mapping.py`**,
so that **there is a single source of truth for the identity mapper**.

**Acceptance Criteria:**

- **Given** `auth/entra.py` **When** I inspect it **Then** `identity_role_mapper` is not defined locally; it is imported from `auth.role_mapping`.
- **Given** `auth/role_mapping.py` **When** I inspect it **Then** `identity_role_mapper` is defined here (unchanged).
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 26.4: Make Auth Factory a True Dict-Dispatch

As a **developer**,
I want **`get_auth()` refactored to use a dict mapping from `auth_type` to a builder callable**,
so that **the auth factory is consistent with the service factory pattern**.

**Acceptance Criteria:**

- **Given** `auth/factory.py` **When** I inspect it **Then** `get_auth()` uses a `dict[str, Callable[[], AuthFunctions]]` mapping from `auth_type` to a builder callable.
- **Given** the Entra branch **When** I inspect the builder **Then** the lazy `httpx` import is preserved inside the builder callable.
- **Given** the application **When** started with `AUTH_TYPE=none` or `AUTH_TYPE=entra` **Then** auth behaviour is unchanged.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 26.5: Cache Service DI Shims

As a **developer**,
I want **service DI shims decorated with `@lru_cache`**,
so that **service dataclasses are built once, consistent with the auth DI approach**.

**Acceptance Criteria:**

- **Given** `services/v1/dummy_service.py` **When** I inspect it **Then** `get_dummy_service_v1()` is decorated with `@lru_cache`.
- **Given** `services/v2/dummy_service.py` **When** I inspect it **Then** `get_dummy_service_v2()` is decorated with `@lru_cache`.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 26.6: Parenthesize Multi-Type `except` in `logging_decorator.py`

As a **developer**,
I want **the bare-comma `except ValueError, TypeError:` changed to the parenthesized form**,
so that **the codebase is consistent and avoids confusion with the Python 2 syntax**.

**Acceptance Criteria:**

- **Given** `aop/logging_decorator.py` line 34 **When** I inspect it **Then** it reads `except (ValueError, TypeError):`.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.
