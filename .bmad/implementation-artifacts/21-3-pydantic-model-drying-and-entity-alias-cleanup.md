# Story 21.3: Pydantic Model DRYing and Entity Alias Cleanup

**Epic:** 21 — Python 3.14 Modernization & Model Cleanup
**Status:** done

## Story

As a **developer**,
I want **a `CamelCaseModel` base for DTOs using `pydantic.alias_generators.to_camel`, and `alias_generator` removed from entity classes**,
so that **DTO configuration is DRY and serialization concerns do not leak into the persistence layer**.

## Acceptance Criteria

- **Given** no custom `_to_camel` function exists anywhere in the codebase **When** I search for `def _to_camel` or `def to_camel` **Then** zero occurrences remain.
- **Given** `models/dto/` **When** I inspect DTO classes **Then** they inherit from a `CamelCaseModel` base (or share a `model_config` that uses `pydantic.alias_generators.to_camel`) **And** `populate_by_name=True` is set.
- **Given** `models/entities/` **When** I inspect entity classes **Then** no `alias_generator` is present on any entity model.
- **Given** `factories/` **When** I inspect factory functions **Then** they correctly map between entities (snake_case) and DTOs (camelCase) without relying on entity aliases.
- **Given** the test suite **When** I run all quality checks **Then** all pass **And** API responses still use camelCase field names.

## Tasks

- [x] Create `CamelCaseModel` base class in `models/dto/` using `pydantic.alias_generators.to_camel`
- [x] Update DTO classes in `models/dto/v1/dummy.py` to inherit from `CamelCaseModel`
- [x] Remove `_to_camel` custom function from all files
- [x] Remove `alias_generator` from entity classes in `models/entities/dummy.py`
- [x] Verify factories still work correctly (entity → DTO mapping)
- [x] Run quality checks and verify all pass
