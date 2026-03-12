# Story 21.1: Remove `from __future__` and Clean Up Import Hygiene

**Epic:** 21 — Python 3.14 Modernization & Model Cleanup
**Status:** done

## Story

As a **developer**,
I want **`from __future__ import annotations` removed from all modules, `# noqa: TC001` suppressions removed, and the `TCH` ruff rule set disabled**,
so that **the codebase reflects Python 3.14 idioms and import hygiene rules match the new reality**.

## Acceptance Criteria

- **Given** all files in `src/` and `tests/` **When** I search for `from __future__ import annotations` **Then** zero occurrences remain.
- **Given** all files **When** I search for `# noqa: TC001` **Then** zero occurrences remain.
- **Given** `pyproject.toml` **When** I inspect ruff's lint `select` **Then** `TCH` is not present.
- **Given** modules that previously used `if TYPE_CHECKING:` guards for imports needed at runtime (Pydantic models, FastAPI dependencies) **When** I inspect them **Then** those imports are at module level (no longer behind `TYPE_CHECKING`).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Remove `from __future__ import annotations` from all src/ and tests/ files
- [x] Remove `# noqa: TC001` suppressions from all files
- [x] Remove `TCH` from ruff lint `select` in pyproject.toml
- [x] Move imports from behind `if TYPE_CHECKING:` guards to module level where needed at runtime
- [x] Run quality checks and fix any issues
