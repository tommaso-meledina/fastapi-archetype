# Epic 27: Documentation, Naming & Script Alignment

Bring documentation, test file names, and scaffolding scripts into alignment with the post-epic-25 codebase.

> **Source:** Post-implementation review of FEEDBACK.md residuals ([NEW_REQUIREMENTS.md](../../../NEW_REQUIREMENTS.md)).
> **Phase:** 4 (Feedback)
> **Depends on:** Epic 26 (code changes may affect documentation content).

## Context

After epics 20–25 (and the code fixes in Epic 26), three non-code gaps remain: `PROJECT_CONTEXT.md` contains stale references to removed patterns, two test files still carry "facade" names from the pre-Epic-24 class hierarchy, and the scaffolding scripts emit patterns the archetype itself has moved away from.

## Problem Statement

- `PROJECT_CONTEXT.md` references `PlainFormatter`, `JsonFormatter`, `SpanFilter` (replaced by structlog), `alias_generator=_to_camel` (replaced by `CamelCaseModel`), and potentially other removed concepts. This creates internal contradictions.
- `tests/auth/test_facade.py` and `tests/auth/test_facade_role_mapper.py` reference the `AuthFacade` concept removed in Epic 24. The test content is correct but the filenames are misleading.
- `scripts/build_template.py` and `scripts/remove_demo.py` still use `from __future__ import annotations` and the custom `_to_camel` function, meaning newly scaffolded projects start with stale patterns.

## Proposed Epic Goal

1. Audit and fix all stale references in `PROJECT_CONTEXT.md`.
2. Rename facade-named test files to reflect their actual test subjects.
3. Update scaffolding scripts to emit current patterns and verify they work against the current codebase.

## Success Criteria

- Zero references to removed patterns (`PlainFormatter`, `JsonFormatter`, `SpanFilter` as custom classes, custom `_to_camel` function, `AuthFacade`, `AuthProvider` ABC, `DummyServiceV*Contract`, `implementations/` subdirectory) in `PROJECT_CONTEXT.md`.
- No internal contradictions in `PROJECT_CONTEXT.md`.
- No test file names reference "facade".
- Zero `from __future__ import annotations` in `scripts/`.
- Generated template uses `CamelCaseModel` + `pydantic.alias_generators.to_camel`, not a custom `_to_camel`.
- `scripts/remove_demo.py` runs successfully against the current codebase.
- `scripts/build_template.py` produces a project that passes `ruff check` and `ruff format --check`.
- All quality checks pass.

## Stories

### Story 27.1: Fix `PROJECT_CONTEXT.md` Internal Contradictions

As a **developer or agent**,
I want **`PROJECT_CONTEXT.md` free of stale references and internal contradictions**,
so that **the authoritative project reference matches the actual codebase**.

**Acceptance Criteria:**

- **Given** `PROJECT_CONTEXT.md` line 92 **When** I inspect it **Then** it describes the current structlog-based implementation (e.g. `configure_logging(settings), structlog processor pipeline, secret redaction`), not the removed `PlainFormatter`, `JsonFormatter`, `SpanFilter` classes.
- **Given** `PROJECT_CONTEXT.md` line 171 **When** I inspect it **Then** it describes DTOs inheriting from `CamelCaseModel` which uses `pydantic.alias_generators.to_camel`, or the redundant sentence is removed (since line 176 already says this correctly).
- **Given** a full-text search of `PROJECT_CONTEXT.md` for `PlainFormatter`, `JsonFormatter`, `SpanFilter` (as custom class names), `_to_camel` (as a custom function), `AuthFacade`, `AuthProvider` ABC, `DummyServiceV*Contract`, or `implementations/` subdirectory **When** I run it **Then** zero matches are found.
- **Given** the project structure tree and inline descriptions in `PROJECT_CONTEXT.md` **When** I compare to the actual codebase **Then** they match.
- **Given** any two sections of `PROJECT_CONTEXT.md` describing the same concept **When** I compare them **Then** they are consistent.

### Story 27.2: Rename Facade-Named Test Files

As a **developer**,
I want **test files renamed to reflect what they actually test**,
so that **file names are not misleading after the facade removal in Epic 24**.

**Acceptance Criteria:**

- **Given** `tests/auth/` **When** I list files **Then** no file name contains "facade".
- **Given** `tests/auth/test_facade.py` **When** I check **Then** it has been renamed to `tests/auth/test_auth_functions.py` (or `test_get_auth.py`).
- **Given** `tests/auth/test_facade_role_mapper.py` **When** I check **Then** it has been renamed to `tests/auth/test_role_mapper.py`.
- **Given** `PROJECT_CONTEXT.md` test structure tree **When** I inspect it **Then** it reflects the renamed files.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

### Story 27.3: Update Scaffolding Scripts for Current Patterns

As a **developer**,
I want **scaffolding scripts updated to emit the current project patterns**,
so that **newly generated projects start with the conventions the archetype itself follows**.

**Acceptance Criteria:**

- **Given** `scripts/build_template.py` and `scripts/remove_demo.py` **When** I search for `from __future__ import annotations` **Then** zero matches are found.
- **Given** `scripts/build_template.py` **When** I inspect the template output logic **Then** it uses `CamelCaseModel` with `pydantic.alias_generators.to_camel` instead of a custom `_to_camel` function.
- **Given** the current codebase **When** I run `python3 scripts/remove_demo.py` **Then** it completes successfully and all remaining tests pass.
- **Given** `scripts/build_template.py` **When** I run `python3 scripts/build_template.py -n "Test Service" -o /tmp` **Then** the generated project passes `ruff check` and `ruff format --check`.
- **Given** the full quality gate **When** I run all quality checks on the archetype itself **Then** all pass.
