# Story 21.2: Replace `type: ignore` with `cast()`

**Epic:** 21 — Python 3.14 Modernization & Model Cleanup
**Status:** done

## Story

As a **developer**,
I want **all `# type: ignore` comments replaced with proper `cast()` calls or the underlying issue resolved**,
so that **type suppression is explicit and narrowly scoped**.

## Acceptance Criteria

- **Given** all files **When** I search for `# type: ignore` **Then** zero occurrences remain.
- **Given** `main.py` and test files that previously used `type: ignore` **When** I inspect them **Then** the issues are resolved via `cast()` from `typing` or by fixing the underlying type.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

## Tasks

- [x] Find all `# type: ignore` occurrences in src/ and tests/
- [x] Replace each with `cast()` or fix the underlying type issue
- [x] Run quality checks and verify all pass
