# Story 19.1: Spec Docs — NFR1 and Architecture References

Status: done

## Story

As a **product or technical owner**,
I want **NFR1 and architecture documentation to require static type checking and to cite both Ruff and ty with version per lock file**,
so that **the requirement is traceable and the tooling is unambiguously defined**.

## Acceptance Criteria

1. **Given** `.bmad/planning-artifacts/prd/non-functional-requirements.md` **When** I read NFR1 **Then** it states that the codebase follows a consistent code style enforced by linting and formatting tools (e.g., ruff) and static type checking (e.g., Astral ty).
2. **Given** `.bmad/planning-artifacts/epics/requirements-inventory.md` **When** I read NFR1 **Then** the same wording as above is used.
3. **Given** `.bmad/planning-artifacts/architecture/architecture-validation-results.md` **When** I read the NFR support table **Then** the NFR1 row specifies both Ruff and ty, with version per lock file (e.g. "Ruff, ty (version per lock file)").
4. **Given** `.bmad/planning-artifacts/architecture/project-context-analysis.md` **When** I read the Code Quality (NFR1–NFR5) description **Then** it includes a sentence that static type checking is enforced via Astral's ty.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — Update NFR1 in non-functional-requirements.md
  - [x] 1.1 Edit `.bmad/planning-artifacts/prd/non-functional-requirements.md`: change NFR1 to state linting/formatting (e.g., ruff) and static type checking (e.g., Astral ty).
- [x] Task 2 (AC: #2) — Update NFR1 in requirements-inventory.md
  - [x] 2.1 Edit `.bmad/planning-artifacts/epics/requirements-inventory.md`: use the same NFR1 wording as in non-functional-requirements.md.
- [x] Task 3 (AC: #3) — Update architecture-validation-results.md NFR table
  - [x] 3.1 Edit `.bmad/planning-artifacts/architecture/architecture-validation-results.md`: in the NFR support table, set NFR1 row to "Ruff, ty (version per lock file)".
- [x] Task 4 (AC: #4) — Update project-context-analysis.md Code Quality
  - [x] 4.1 Edit `.bmad/planning-artifacts/architecture/project-context-analysis.md`: in the Code Quality (NFR1–NFR5) bullet, add a sentence that static type checking is enforced via Astral's ty.

## Dev Notes

- All changes are documentation-only in `.bmad/planning-artifacts/`. No application code or tests.
- Preserve existing structure, section headers, and formatting; only update the specified NFR1/Code Quality text.
- Source: Epic 19 — `.bmad/planning-artifacts/epics/epic-19-static-type-checking-with-ty.md`.

### References

- [Source: .bmad/planning-artifacts/epics/epic-19-static-type-checking-with-ty.md]
- [Source: .bmad/planning-artifacts/prd/non-functional-requirements.md]
- [Source: .bmad/planning-artifacts/architecture/architecture-validation-results.md]
- [Source: .bmad/planning-artifacts/architecture/project-context-analysis.md]

## Dev Agent Record

### Agent Model Used

-

### Debug Log References

### Completion Notes List

### File List

- .bmad/planning-artifacts/prd/non-functional-requirements.md (modified)
- .bmad/planning-artifacts/epics/requirements-inventory.md (modified)
- .bmad/planning-artifacts/architecture/architecture-validation-results.md (modified)
- .bmad/planning-artifacts/architecture/project-context-analysis.md (modified)
