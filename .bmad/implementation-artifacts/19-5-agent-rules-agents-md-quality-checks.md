# Story 19.5: Agent Rules — AGENTS.md Quality Checks

Status: ready-for-dev

## Story

As a **maintainer or agent**,
I want **AGENTS.md to define quality checks to include ty check and to require fixing both errors and warnings from ty**,
so that **agents and humans run type checking before commit and treat warnings as mandatory to fix**.

## Acceptance Criteria

1. **Given** `AGENTS.md` **When** I read the section that requires quality checks before commit **Then** it explicitly includes `ty check` in the set of quality checks (alongside ruff check, ruff format, and the full test suite).
2. **Given** `AGENTS.md` **When** I read the guidance on type checking **Then** it states that both errors and warnings from ty must be fixed (no blanket suppressions unless justified and documented). Do not modify `CLAUDE.md` (it is a symlink to AGENTS.md).

## Tasks / Subtasks

- [x] Task 1 (AC: #1, #2) — Update AGENTS.md
  - [x] 1.1 Define quality checks to include ruff check, ruff format, ty check, and full test suite.
  - [x] 1.2 Add guidance: both errors and warnings from ty must be fixed; no blanket suppressions unless justified and documented.

## Dev Agent Record

### File List

- AGENTS.md (modified)
