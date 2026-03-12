# Story 20.3: Model and Dataclass Improvements

**Epic:** 20 — Hygiene & Quick Wins
**Status:** in-progress

## Story

As a **developer**,
I want **`_default_uuid` simplified, `kw_only=True` on dataclasses, and `slots=True` removed from `Principal`**,
so that **model definitions are cleaner and more Pythonic**.

## Acceptance Criteria

- **Given** `models/entities/dummy.py` **When** I inspect `_default_uuid` **Then** it is a lambda or the field uses a direct call (no `default_factory` pointing to a named wrapper function).
- **Given** `auth/models.py` and `core/constants.py` **When** I inspect `Principal` and `ResourceDefinition` **Then** both dataclasses use `kw_only=True`.
- **Given** `auth/models.py` **When** I inspect `Principal` **Then** `slots=True` is not present.
- **Given** the test suite **When** I run `uv run pytest` **Then** all tests pass.

## Tasks

- [x] Replace `_default_uuid` function with inline lambda in `models/entities/dummy.py`
- [x] Add `kw_only=True` to `ResourceDefinition` in `core/constants.py`
- [x] Remove `slots=True` and add `kw_only=True` to `Principal` in `auth/models.py`
