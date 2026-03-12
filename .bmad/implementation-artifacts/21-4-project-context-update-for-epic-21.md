# Story 21.4: PROJECT_CONTEXT Update for Epic 21

**Epic:** 21 — Python 3.14 Modernization & Model Cleanup
**Status:** done

## Story

As a **developer or agent**,
I want **`PROJECT_CONTEXT.md` updated to reflect the new conventions introduced in this epic**,
so that **documentation matches the codebase and agents follow the correct patterns**.

## Acceptance Criteria

- **Given** `PROJECT_CONTEXT.md` § Code style **When** I read it **Then** the `from __future__ import annotations` convention is removed.
- **Given** `PROJECT_CONTEXT.md` § Anti-Patterns **When** I read it **Then** "Do not skip `from __future__ import annotations`" is removed.
- **Given** `PROJECT_CONTEXT.md` § Code Quality **When** I read the ruff rules list **Then** `TCH` is not listed.
- **Given** `PROJECT_CONTEXT.md` **When** I read model/DTO conventions **Then** `CamelCaseModel` base, `pydantic.alias_generators`, and entity alias removal are documented.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Remove `from __future__ import annotations` convention from § Code style
- [x] Remove "Do not skip `from __future__ import annotations`" from § Anti-Patterns
- [x] Remove `TCH` from § Code Quality ruff rules list
- [x] Document `CamelCaseModel`, `pydantic.alias_generators.to_camel`, entity alias removal in model/DTO conventions
- [x] Run quality checks and verify all pass
