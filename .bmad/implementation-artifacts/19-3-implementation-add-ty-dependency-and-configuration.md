# Story 19.3: Implementation — Add ty Dependency and Configuration

Status: done

## Story

As a **software engineer**,
I want **ty added as a dev dependency and configured in pyproject.toml with explicit include for src and tests**,
so that **type checking runs over the same paths as Ruff and uses the project's Python version**.

## Acceptance Criteria

1. **Given** `pyproject.toml` **When** I inspect the dev dependency group **Then** it includes the `ty` package (Astral). Use the latest version available at implementation time; revisit the version if compatibility issues arise.
2. **Given** `pyproject.toml` **When** I look for `[tool.ty]` **Then** it contains:
   - `[tool.ty.environment]` with `python-version = "3.14"`.
   - `[tool.ty.src]` with `include = ["src", "tests"]` (mirroring the scope used for Ruff).
3. **Given** I run `uv sync` **Then** ty is installed in the dev environment **And** `uv run ty check` executes (it may report diagnostics until Story 19.6).

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Add ty to dev dependency group
  - [x] 1.1 Add `ty` to `[dependency-groups] dev` in pyproject.toml (latest version at implementation time).
- [x] Task 2 (AC: #2, #3) — Add [tool.ty] configuration
  - [x] 2.1 Add `[tool.ty.environment]` with `python-version = "3.14"`.
  - [x] 2.2 Add `[tool.ty.src]` with `include = ["src", "tests"]`.
  - [x] 2.3 Run `uv sync` and verify `uv run ty check` executes.

## Dev Notes

- Ruff uses `src = ["src"]` in this project; tests live in `tests/`. Epic requires include for both src and tests.
- Source: Epic 19 — `.bmad/planning-artifacts/epics/epic-19-static-type-checking-with-ty.md`.

## Dev Agent Record

### Agent Model Used

-

### File List

- pyproject.toml (modified)
