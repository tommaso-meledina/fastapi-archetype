# Story 18.1: Add Profile to Configuration

Status: ready-for-dev

## Story

As a **developer or operator**,
I want **an optional `PROFILE` environment variable (`"default"` or `"mock"`) with default `"default"`**,
so that **the application can later wire service implementations based on profile**.

## Acceptance Criteria

1. **Given** `core/config.py` **When** this story is complete **Then** `AppSettings` has a field `profile` with type `Literal["default", "mock"]` and default `"default"` **And** the field is validated so that only these two values are accepted (fail fast at startup if invalid).
2. **Given** `.env.example` **When** I read it **Then** it documents optional `PROFILE` with allowed values and default behaviour.
3. **Given** the test suite **When** I run tests that load config **Then** they are updated if they previously assumed no `profile` field (e.g. assert default or explicit profile).

## Tasks / Subtasks

- [ ] Task 1 (AC: 1) — Add `profile` to AppSettings
  - [ ] Add `profile: Literal["default", "mock"]` with default `"default"`.
  - [ ] Add field validator so only `"default"` and `"mock"` are accepted; raise `ValueError` (fail fast) for invalid values.
- [ ] Task 2 (AC: 2) — Document PROFILE in .env.example
  - [ ] Add PROFILE entry with allowed values and default behaviour (match existing .env.example style).
- [ ] Task 3 (AC: 3) — Update config tests
  - [ ] Add tests for profile default and valid values; add test for invalid PROFILE raising.

## Dev Notes

- PROJECT_CONTEXT §11 and §Conventions (Configuration) describe profile: optional `PROFILE`, values `"default"` | `"mock"`, default `"default"`. Typed field on `AppSettings`.
- Follow existing config pattern: `Literal` for constrained values; use `@field_validator` and raise `ValueError` for invalid (like `log_level`), not fallback like `log_mode`.
- `.env.example` format: comment line with variable name, default, and allowed values (see LOG_MODE, AUTH_TYPE).
- tests/core/test_config.py: add tests for `profile` default, valid "default"/"mock", and invalid value raising ValidationError.

### References

- [Source: PROJECT_CONTEXT.md §11 Profile and Service Contracts]
- [Source: .bmad/planning-artifacts/epics/epic-18-profile-and-service-contracts.md Story 18.1]
