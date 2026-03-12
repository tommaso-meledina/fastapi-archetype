# Story 27.2: Rename Facade-Named Test Files

## Status: done

## Story

As a **developer**,
I want **test files renamed to reflect what they actually test**,
so that **file names are not misleading after the facade removal in Epic 24**.

## Acceptance Criteria

- **Given** `tests/auth/` **When** I list files **Then** no file name contains "facade". ✅
- **Given** `tests/auth/test_facade.py` **When** I check **Then** it has been renamed to `tests/auth/test_auth_functions.py`. ✅
- **Given** `tests/auth/test_facade_role_mapper.py` **When** I check **Then** it has been renamed to `tests/auth/test_role_mapper.py`. ✅
- **Given** `PROJECT_CONTEXT.md` test structure tree **When** I inspect it **Then** it reflects the renamed files. ✅
- **Given** the full quality gate **When** I run all quality checks **Then** all pass. ✅

## Tasks

- [x] Rename `tests/auth/test_facade.py` → `tests/auth/test_auth_functions.py` (via `git mv`)
- [x] Rename `tests/auth/test_facade_role_mapper.py` → `tests/auth/test_role_mapper.py` (via `git mv`)
- [x] Update `PROJECT_CONTEXT.md` test structure tree to reflect new file names
