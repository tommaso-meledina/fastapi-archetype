# Story 19.2: Architectural Decision — Extend AD 23 for Type Checking

Status: done

## Story

As a **developer or architect**,
I want **AD 23 (Code Quality Tooling) in ARCH_DECISIONS.md to document the choice of ty for static type checking**,
so that **the decision is recorded and future changes have a clear rationale**.

## Acceptance Criteria

1. **Given** `ARCH_DECISIONS.md` **When** I read AD 23 **Then** the context includes the need for static type checking to be enforced.
2. **Given** AD 23 **When** I read the options **Then** there is an option (or extended consideration) for type checking that includes ty (same ecosystem as uv/Ruff, fast, config in `pyproject.toml`) and alternatives (e.g. mypy, Pyright).
3. **Given** AD 23 **When** I read the decision **Then** it states that ty is used for type checking, configured under `[tool.ty]` in `pyproject.toml`, and that quality checks include `uv run ty check` in addition to Ruff lint and format.

## Tasks / Subtasks

- [x] Task 1 (AC: #1, #2, #3) — Extend AD 23 in ARCH_DECISIONS.md
  - [x] 1.1 Update Context: add that static type checking must be enforced alongside linting and formatting.
  - [x] 1.2 Add type-checking options: ty (same ecosystem as uv/Ruff, fast, config in pyproject.toml) and alternatives (e.g. mypy, Pyright).
  - [x] 1.3 Update Decision: state ty is used for type checking, configured under `[tool.ty]` in pyproject.toml; quality checks include `uv run ty check` in addition to Ruff lint and format.

## Dev Notes

- Single file: `ARCH_DECISIONS.md`. Preserve existing AD 23 structure (Context, Options table, Decision).
- Source: Epic 19 — `.bmad/planning-artifacts/epics/epic-19-static-type-checking-with-ty.md`.

### References

- [Source: .bmad/planning-artifacts/epics/epic-19-static-type-checking-with-ty.md]

## Dev Agent Record

### Agent Model Used

-

### Debug Log References

### Completion Notes List

### File List

- ARCH_DECISIONS.md (modified)
