# Story 19.4: Documentation — PROJECT_CONTEXT and README

Status: ready-for-dev

## Story

As a **developer**,
I want **PROJECT_CONTEXT and README to list ty and define quality checks as ruff + ty + tests**,
so that **I know how to run type checking and what "quality checks" means**.

## Acceptance Criteria

1. **Given** `PROJECT_CONTEXT.md` **When** I read the Technology Stack → Dev table **Then** there is a row for ty (version per lock file) with role "Type checking".
2. **Given** `PROJECT_CONTEXT.md` **When** I read §14 Code Quality **Then** it states that type checking is enforced with Astral's ty (targeting the project's Python version) **And** it lists the three code-quality commands: ruff check, ruff format --check, and ty check **And** it defines quality checks to include the full test suite as well.
3. **Given** `README.md` **When** I read the Code Quality section **Then** it states that type checking is enforced with Astral's ty **And** the command block includes `uv run ty check` together with the existing ruff commands.

## Tasks / Subtasks

- [x] Task 1 (AC: #1, #2) — Update PROJECT_CONTEXT
  - [x] 1.1 Add ty to Dev table (version per lock file, role "Type checking").
  - [x] 1.2 Update §14: type checking with ty, list ruff check, ruff format --check, ty check, define quality checks including full test suite.
- [x] Task 2 (AC: #3) — Update README Code Quality
  - [x] 2.1 Mention ty and add `uv run ty check` to command block.

## Dev Agent Record

### File List

- PROJECT_CONTEXT.md (modified)
- README.md (modified)
