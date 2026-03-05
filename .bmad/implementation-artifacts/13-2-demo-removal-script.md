# Story 13.2: Demo Removal Script

Status: ready-for-dev

## Story

As a **software engineer creating a new service from the archetype**,
I want **to run `python3 scripts/remove_demo.py` and have all Dummy CRUD boilerplate removed automatically**,
So that **I start with a clean project that has all infrastructure intact, structural scaffolding in place, and all tests passing — without manually hunting for demo code across the codebase**.

## Acceptance Criteria

1. **Given** the git working tree has uncommitted changes
   **When** I run `python3 scripts/remove_demo.py`
   **Then** the script prints an informative error and exits non-zero without modifying any files

2. **Given** the git working tree is clean
   **When** I run `python3 scripts/remove_demo.py`
   **Then** the following 9 files are deleted:
   - `src/fastapi_archetype/models/dummy.py`
   - `src/fastapi_archetype/api/v1/dummy_routes.py`
   - `src/fastapi_archetype/api/v2/dummy_routes.py`
   - `src/fastapi_archetype/services/v1/dummy_service.py`
   - `src/fastapi_archetype/services/v2/dummy_service.py`
   - `tests/api/test_dummy_routes.py`
   - `tests/api/test_v2_dummy_routes.py`
   - `tests/services/v1/test_dummy_service.py`
   - `tests/services/v2/test_dummy_service.py`

3. **Given** the script has executed successfully
   **When** I inspect the surgically edited shared files
   **Then** the following edits have been made:
   - `core/constants.py`: `DUMMIES` ResourceDefinition removed
   - `core/errors.py`: `DUMMY_NOT_FOUND` removed from ErrorCode enum
   - `core/config.py`: `rate_limit_get_dummies` and `rate_limit_post_dummies` removed
   - `services/__init__.py`: dummy service imports and apply_logging calls removed
   - `api/v1/__init__.py`: dummy router import and include removed
   - `api/v2/__init__.py`: dummy router import and include removed
   - `observability/prometheus.py`: `dummies_created_total` counter removed from Counters/Metrics
   - `.env.example`: `RATE_LIMIT_GET_DUMMIES` and `RATE_LIMIT_POST_DUMMIES` lines removed
   - All edited files remain syntactically valid

4. **Given** the script has executed successfully
   **When** I inspect the version directories
   **Then** `api/v1/`, `api/v2/`, `services/v1/`, `services/v2/` still exist with valid `__init__.py`

5. **Given** the script has executed successfully
   **When** I start the application
   **Then** it starts without errors; `/health`, `/metrics`, `/docs`, `/redoc` are reachable

6. **Given** the script has executed successfully
   **When** I run the full test suite
   **Then** all remaining tests pass

7. **Given** the script implementation
   **When** I inspect `scripts/remove_demo.py`
   **Then** it is a single Python 3 file with no dependencies beyond the standard library

## Tasks / Subtasks

- [ ] Task 1 — Create `scripts/remove_demo.py` (AC: #1, #2, #3, #4, #7)
  - [ ] 1.1 Implement git working tree clean check
  - [ ] 1.2 Implement file deletion for the 9 demo files
  - [ ] 1.3 Implement surgical edits for constants.py (remove DUMMIES)
  - [ ] 1.4 Implement surgical edits for errors.py (remove DUMMY_NOT_FOUND)
  - [ ] 1.5 Implement surgical edits for config.py (remove rate limit fields)
  - [ ] 1.6 Implement surgical edits for services/__init__.py (remove dummy imports/logging)
  - [ ] 1.7 Implement surgical edits for api/v1/__init__.py and api/v2/__init__.py
  - [ ] 1.8 Implement surgical edits for prometheus.py (remove dummies_created_total)
  - [ ] 1.9 Implement surgical edits for .env.example
  - [ ] 1.10 Ensure version directories retain valid __init__.py
- [ ] Task 2 — Test the script end-to-end (AC: #1, #2, #3, #4, #5, #6)
  - [ ] 2.1 Test dirty-tree guard (script rejects uncommitted changes)
  - [ ] 2.2 Test full removal: run script, verify deletions, verify edits, run test suite
  - [ ] 2.3 Reset working tree after testing

## Dev Notes

- **stdlib only**: Use `subprocess`, `pathlib`, `os`, `sys`, `re` — no third-party imports.
- **Git check**: `git diff --quiet HEAD` and `git diff --cached --quiet HEAD` to detect dirty tree.
- **File surgery approach**: Read file content, apply targeted string replacements or line removals, write back. Use exact string matching where possible; regex only where line patterns vary.
- **Target files for surgical edits** (all paths relative to project root):
  - `src/fastapi_archetype/core/constants.py` — remove `DUMMIES = ResourceDefinition(...)` block (lines 11-15)
  - `src/fastapi_archetype/core/errors.py` — remove `DUMMY_NOT_FOUND = (...)` line (line 19)
  - `src/fastapi_archetype/core/config.py` — remove `rate_limit_get_dummies` and `rate_limit_post_dummies` fields (lines 51-52)
  - `src/fastapi_archetype/services/__init__.py` — remove all 4 lines of dummy service imports/apply_logging
  - `src/fastapi_archetype/api/v1/__init__.py` — remove dummy_router import and include_router call
  - `src/fastapi_archetype/api/v2/__init__.py` — remove dummy_router import and include_router call
  - `src/fastapi_archetype/observability/prometheus.py` — remove Counters class body, Metrics.counters field, and metrics singleton
  - `.env.example` — remove rate limit comment lines for dummies

### References

- [Source: .bmad/planning-artifacts/epics/epic-13-demo-removal.md#Story 13.2]
- [Source: PROJECT_CONTEXT.md#Project Structure]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking (Cursor)

### Debug Log References

### Completion Notes List

### File List
