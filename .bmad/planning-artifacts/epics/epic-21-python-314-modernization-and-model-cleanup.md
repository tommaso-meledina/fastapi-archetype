# Epic 21: Python 3.14 Modernization & Model Cleanup

Align the codebase with Python 3.14 idioms and DRY up the Pydantic model layer. Covers `from __future__` removal, ruff `TCH` rule removal, `type: ignore` cleanup, and the introduction of a shared `CamelCaseModel` base using `pydantic.alias_generators` (see [NEXT_STEPS.md](../../../NEXT_STEPS.md) actions 10–16, 48).

## Context

The project targets Python >=3.14, where `from __future__ import annotations` is a no-op. The codebase currently imports it in every module, gates type-checking imports behind `TYPE_CHECKING` (enforced by ruff's `TCH` rule set), and uses custom `_to_camel` alias generator functions repeated across modules. Entity models carry `alias_generator` for camelCase serialization, which leaks a DTO concern into the persistence layer.

## Problem Statement

- **Stale `from __future__`:** Every module imports `from __future__ import annotations`, which is unnecessary on Python 3.14 and misleading to contributors.
- **`TCH` rule and `noqa: TC001` clutter:** The ruff `TCH` rule set forces imports used only in annotations behind `TYPE_CHECKING` guards. With `from __future__` removed, annotated types are evaluated at runtime (especially for Pydantic/FastAPI), making `TYPE_CHECKING` guards actively harmful for those imports. The `# noqa: TC001` suppressions exist precisely because of this conflict.
- **`type: ignore` instead of `cast()`:** Several modules use `# type: ignore` to suppress type checker diagnostics instead of properly narrowing with `cast()`.
- **Repeated `_to_camel`:** Custom camelCase functions are duplicated; `pydantic.alias_generators.to_camel` is a drop-in.
- **No shared DTO base:** Each DTO repeats its `model_config`; a `CamelCaseModel` base would DRY this up.
- **Entity alias leakage:** Entity classes carry `alias_generator=_to_camel`, which is a serialization concern that leaks into the DB layer.

## Proposed Epic Goal

1. Remove `from __future__ import annotations` from all source and test files.
2. Remove `# noqa: TC001` suppressions (now unnecessary).
3. Remove the `TCH` rule set from ruff configuration.
4. Replace `type: ignore` with `cast()` where the type issue cannot be resolved.
5. Replace custom `_to_camel` with `pydantic.alias_generators.to_camel`.
6. Create a `CamelCaseModel` base class for DTOs.
7. Remove `alias_generator` from entity classes; adjust factories.
8. Update `PROJECT_CONTEXT.md` with a targeted checklist of sections.

## Success Criteria

- Zero occurrences of `from __future__ import annotations` in the codebase.
- Zero occurrences of `# noqa: TC001` in the codebase.
- `TCH` is removed from the ruff `select` list in `pyproject.toml`.
- Zero occurrences of `# type: ignore` (replaced with `cast()` or resolved).
- No custom `_to_camel` function exists; DTOs use `pydantic.alias_generators.to_camel` via `CamelCaseModel`.
- Entity classes have no `alias_generator`; factories handle DTO ↔ entity mapping without relying on entity aliases.
- `PROJECT_CONTEXT.md` is updated per the action 16 checklist.
- All quality checks pass.

## Stories

### Story 21.1: Remove `from __future__` and Clean Up Import Hygiene

As a **developer**,
I want **`from __future__ import annotations` removed from all modules, `# noqa: TC001` suppressions removed, and the `TCH` ruff rule set disabled**,
so that **the codebase reflects Python 3.14 idioms and import hygiene rules match the new reality**.

**Acceptance Criteria:**

- **Given** all files in `src/` and `tests/` **When** I search for `from __future__ import annotations` **Then** zero occurrences remain.
- **Given** all files **When** I search for `# noqa: TC001` **Then** zero occurrences remain.
- **Given** `pyproject.toml` **When** I inspect ruff's lint `select` **Then** `TCH` is not present.
- **Given** modules that previously used `if TYPE_CHECKING:` guards for imports needed at runtime (Pydantic models, FastAPI dependencies) **When** I inspect them **Then** those imports are at module level (no longer behind `TYPE_CHECKING`).
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 21.2: Replace `type: ignore` with `cast()`

As a **developer**,
I want **all `# type: ignore` comments replaced with proper `cast()` calls or the underlying issue resolved**,
so that **type suppression is explicit and narrowly scoped**.

**Acceptance Criteria:**

- **Given** all files **When** I search for `# type: ignore` **Then** zero occurrences remain.
- **Given** `main.py` and test files that previously used `type: ignore` **When** I inspect them **Then** the issues are resolved via `cast()` from `typing` or by fixing the underlying type.
- **Given** the test suite **When** I run all quality checks **Then** all pass.

### Story 21.3: Pydantic Model DRYing and Entity Alias Cleanup

As a **developer**,
I want **a `CamelCaseModel` base for DTOs using `pydantic.alias_generators.to_camel`, and `alias_generator` removed from entity classes**,
so that **DTO configuration is DRY and serialization concerns do not leak into the persistence layer**.

**Acceptance Criteria:**

- **Given** no custom `_to_camel` function exists anywhere in the codebase **When** I search for `def _to_camel` or `def to_camel` **Then** zero occurrences remain.
- **Given** `models/dto/` **When** I inspect DTO classes **Then** they inherit from a `CamelCaseModel` base (or share a `model_config` that uses `pydantic.alias_generators.to_camel`) **And** `populate_by_name=True` is set.
- **Given** `models/entities/` **When** I inspect entity classes **Then** no `alias_generator` is present on any entity model.
- **Given** `factories/` **When** I inspect factory functions **Then** they correctly map between entities (snake_case) and DTOs (camelCase) without relying on entity aliases.
- **Given** the test suite **When** I run all quality checks **Then** all pass **And** API responses still use camelCase field names.

### Story 21.4: PROJECT_CONTEXT Update for Epic 21

As a **developer or agent**,
I want **`PROJECT_CONTEXT.md` updated to reflect the new conventions introduced in this epic**,
so that **documentation matches the codebase and agents follow the correct patterns**.

**Acceptance Criteria:**

- **Given** `PROJECT_CONTEXT.md` § Code style **When** I read it **Then** the `from __future__ import annotations` convention is removed.
- **Given** `PROJECT_CONTEXT.md` § Anti-Patterns **When** I read it **Then** "Do not skip `from __future__ import annotations`" is removed.
- **Given** `PROJECT_CONTEXT.md` § Code Quality **When** I read the ruff rules list **Then** `TCH` is not listed.
- **Given** `PROJECT_CONTEXT.md` **When** I read model/DTO conventions **Then** `CamelCaseModel` base, `pydantic.alias_generators`, and entity alias removal are documented.
- **Given** the full quality gate **When** I run all quality checks **Then** all pass.
