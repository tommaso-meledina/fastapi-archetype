# Story 23.2: Test Suite Cleanup

**Status:** in-progress

## Story

As a **developer**,
I want **dedicated mock-implementation tests removed, mock files excluded from coverage, and large test classes split into files**,
so that **the test suite is leaner and follows pytest conventions**.

## Acceptance Criteria

- **Given** `tests/services/` **When** I inspect it **Then** no dedicated unit tests for mock service implementations exist.
- **Given** `tests/services/` **When** I inspect it **Then** at least one integration test per service version (v1, v2) verifies profile-switching.
- **Given** `pyproject.toml` **When** I inspect coverage configuration **Then** mock implementation files are excluded.
- **Given** `tests/observability/` and `tests/auth/` **When** I inspect them **Then** formerly large test classes are reorganized into separate files.
- **Given** the test suite **When** I run all quality checks **Then** all pass **And** coverage remains at or above the project target (>90%).

## Tasks

- [x] Remove tests/services/v1/test_mock_dummy_service.py
- [x] Remove tests/services/v2/test_mock_dummy_service.py
- [x] Verify profile-switching integration tests exist in tests/api/test_profile_service_selection.py
- [x] Add coverage exclude for mock implementation files to pyproject.toml
- [x] Split tests/observability/test_logging.py classes into separate files
- [x] Split tests/auth/test_dependencies.py classes into separate files
- [x] Split tests/auth/test_role_mapping.py classes into separate files
- [x] All quality checks pass, coverage >=90%
