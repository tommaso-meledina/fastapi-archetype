# Epic 19: Static Type Checking with Astral ty

A developer runs a single type checker (Astral's ty) as part of the project's quality gates. Type checking is enforced alongside Ruff lint/format: all diagnostics (errors and warnings) must be fixed so that `uv run ty check` passes with zero output. Spec docs, architecture decisions, and implementation are updated so that ty is a documented, committed part of the stack.

## Context

The project currently enforces only Ruff (lint and format) and pytest. Static type checking is not enforced; the codebase uses type annotations and `TYPE_CHECKING` patterns but no type checker runs in quality checks. Introducing ty aligns with the existing Astral/uv ecosystem and makes type safety a first-class gate.

## Problem Statement

- **No type safety gate:** Annotations are not validated; type errors can slip in and go undetected until runtime or code review.
- **Spec and arch docs omit type checking:** NFR1 and architecture validation refer only to linting; AD 23 describes only Ruff. New contributors and agents have no mandate to run or fix type-check results.
- **Quality checks undefined for type checking:** PROJECT_CONTEXT, README, and AGENTS.md do not list a type checker; "quality checks" are ambiguous.

## Proposed Epic Goal

1. **Extend NFR1** in the PRD and requirements inventory to include static type checking (e.g., Astral ty).
2. **Update architecture docs:** Architecture validation table (NFR1 row) and project-context analysis to reference ty and Ruff with "version per lock file" for both tools.
3. **Extend AD 23** in ARCH_DECISIONS.md to add type checking: context, option (ty vs alternatives), decision (ty, configured in `pyproject.toml`).
4. **Add ty to the implementation:** Dev dependency in `pyproject.toml` (ty, latest available at implementation time; revisit if compatibility issues arise), `[tool.ty]` config with explicit `include` for `src` and `tests` (mirroring Ruff), Python version 3.14.
5. **Document ty in PROJECT_CONTEXT:** Dev table and §14 Code Quality; define quality checks as ruff check + ruff format + ty check + test suite.
6. **Document ty in README:** Code Quality section and commands.
7. **Update AGENTS.md:** Define "quality checks" to include `ty check` (and that both errors and warnings must be fixed). Do not change CLAUDE.md (it is a symlink to AGENTS.md).
8. **Fix the codebase:** Resolve all ty diagnostics (errors and warnings) so that `uv run ty check` passes with zero output.

## Success Criteria

- NFR1 in PRD and requirements inventory explicitly includes static type checking (e.g., Astral ty).
- Architecture validation and project-context analysis mention ty and Ruff with version per lock file.
- AD 23 in ARCH_DECISIONS.md documents the decision to use ty for type checking.
- `pyproject.toml` includes ty in the dev dependency group and has a `[tool.ty]` section with `include = ["src", "tests"]` and `python-version = "3.14"`.
- PROJECT_CONTEXT lists ty in the Dev table and §14; quality checks are defined as ruff check, ruff format --check, ty check, and full test suite.
- README Code Quality section describes ty and shows `uv run ty check`.
- AGENTS.md states that before each commit all quality checks (including `ty check`) must pass and that both errors and warnings from ty must be fixed.
- `uv run ty check` passes with zero diagnostics; no suppressions except where explicitly justified and documented.

## Stories

### Story 19.1: Spec Docs — NFR1 and Architecture References

As a **product or technical owner**,
I want **NFR1 and architecture documentation to require static type checking and to cite both Ruff and ty with version per lock file**,
so that **the requirement is traceable and the tooling is unambiguously defined**.

**Acceptance Criteria:**

- **Given** `.bmad/planning-artifacts/prd/non-functional-requirements.md` **When** I read NFR1 **Then** it states that the codebase follows a consistent code style enforced by linting and formatting tools (e.g., ruff) and static type checking (e.g., Astral ty).
- **Given** `.bmad/planning-artifacts/epics/requirements-inventory.md` **When** I read NFR1 **Then** the same wording as above is used.
- **Given** `.bmad/planning-artifacts/architecture/architecture-validation-results.md` **When** I read the NFR support table **Then** the NFR1 row specifies both Ruff and ty, with version per lock file (e.g. "Ruff, ty (version per lock file)").
- **Given** `.bmad/planning-artifacts/architecture/project-context-analysis.md` **When** I read the Code Quality (NFR1–NFR5) description **Then** it includes a sentence that static type checking is enforced via Astral's ty.

### Story 19.2: Architectural Decision — Extend AD 23 for Type Checking

As a **developer or architect**,
I want **AD 23 (Code Quality Tooling) in ARCH_DECISIONS.md to document the choice of ty for static type checking**,
so that **the decision is recorded and future changes have a clear rationale**.

**Acceptance Criteria:**

- **Given** `ARCH_DECISIONS.md` **When** I read AD 23 **Then** the context includes the need for static type checking to be enforced.
- **Given** AD 23 **When** I read the options **Then** there is an option (or extended consideration) for type checking that includes ty (same ecosystem as uv/Ruff, fast, config in `pyproject.toml`) and alternatives (e.g. mypy, Pyright).
- **Given** AD 23 **When** I read the decision **Then** it states that ty is used for type checking, configured under `[tool.ty]` in `pyproject.toml`, and that quality checks include `uv run ty check` in addition to Ruff lint and format.

### Story 19.3: Implementation — Add ty Dependency and Configuration

As a **software engineer**,
I want **ty added as a dev dependency and configured in pyproject.toml with explicit include for src and tests**,
so that **type checking runs over the same paths as Ruff and uses the project's Python version**.

**Acceptance Criteria:**

- **Given** `pyproject.toml` **When** I inspect the dev dependency group **Then** it includes the `ty` package (Astral). Use the latest version available at implementation time; revisit the version if compatibility issues arise.
- **Given** `pyproject.toml` **When** I look for `[tool.ty]` **Then** it contains:
  - `[tool.ty.environment]` with `python-version = "3.14"`.
  - `[tool.ty.src]` with `include = ["src", "tests"]` (mirroring the scope used for Ruff).
- **Given** I run `uv sync` **Then** ty is installed in the dev environment **And** `uv run ty check` executes (it may report diagnostics until Story 19.6).

### Story 19.4: Documentation — PROJECT_CONTEXT and README

As a **developer**,
I want **PROJECT_CONTEXT and README to list ty and define quality checks as ruff + ty + tests**,
so that **I know how to run type checking and what "quality checks" means**.

**Acceptance Criteria:**

- **Given** `PROJECT_CONTEXT.md` **When** I read the Technology Stack → Dev table **Then** there is a row for ty (version per lock file) with role "Type checking".
- **Given** `PROJECT_CONTEXT.md` **When** I read §14 Code Quality **Then** it states that type checking is enforced with Astral's ty (targeting the project's Python version) **And** it lists the three code-quality commands: ruff check, ruff format --check, and ty check **And** it defines quality checks to include the full test suite as well.
- **Given** `README.md` **When** I read the Code Quality section **Then** it states that type checking is enforced with Astral's ty **And** the command block includes `uv run ty check` together with the existing ruff commands.

### Story 19.5: Agent Rules — AGENTS.md Quality Checks

As a **maintainer or agent**,
I want **AGENTS.md to define quality checks to include ty check and to require fixing both errors and warnings from ty**,
so that **agents and humans run type checking before commit and treat warnings as mandatory to fix**.

**Acceptance Criteria:**

- **Given** `AGENTS.md` **When** I read the section that requires quality checks before commit **Then** it explicitly includes `ty check` in the set of quality checks (alongside ruff check, ruff format, and the full test suite).
- **Given** `AGENTS.md` **When** I read the guidance on type checking **Then** it states that both errors and warnings from ty must be fixed (no blanket suppressions unless justified and documented). Do not modify `CLAUDE.md` (it is a symlink to AGENTS.md).

### Story 19.6: Codebase — Fix All ty Diagnostics (Errors and Warnings)

As a **software engineer**,
I want **all ty diagnostics (errors and warnings) resolved so that `uv run ty check` passes with zero output**,
so that **type safety is enforced and the codebase is clean for future changes**.

**Acceptance Criteria:**

- **Given** I run `uv run ty check` **When** the command completes **Then** it exits with code 0 **And** it produces no error or warning diagnostics.
- **Given** the codebase **When** I look for type-check suppressions **Then** there are no broad or unjustified suppressions; any `ty: ignore` or rule downgrades in config are minimal, justified, and documented (e.g. in comments or PROJECT_CONTEXT).
- **Given** the full quality gate **When** I run ruff check, ruff format --check, ty check, and pytest **Then** all pass.

## Notes

- **Version:** Add ty with the latest version available at implementation time; if compatibility issues appear (e.g. with Python 3.14 or a dependency), revisit the version or report upstream and document in the epic or a follow-up.
- **Ruff vs ty:** Ruff remains the single tool for lint and format; ty is added only for type checking. TCH (type-checking import style) in Ruff is unchanged.
- **Epic list:** After this epic is created, add Epic 19 to `.bmad/planning-artifacts/epics/epic-list.md` with a one-line summary and "NFRs addressed: NFR1" (extension of NFR1).
