# Story 27.3: Update Scaffolding Scripts for Current Patterns

## Status: done

## Story

As a **developer**,
I want **scaffolding scripts updated to emit the current project patterns**,
so that **newly generated projects start with the conventions the archetype itself follows**.

## Acceptance Criteria

- **Given** `scripts/build_template.py` and `scripts/remove_demo.py` **When** I search for `from __future__ import annotations` **Then** zero matches are found. ✅
- **Given** `scripts/build_template.py` **When** I inspect the template output logic **Then** it uses `CamelCaseModel` with `pydantic.alias_generators.to_camel` instead of a custom `_to_camel` function. ✅
- **Given** the current codebase **When** I run `python3 scripts/remove_demo.py` **Then** it completes successfully and all remaining tests pass (156 tests). ✅
- **Given** `scripts/build_template.py` **When** I run it **Then** the generated project passes `ruff check` and `ruff format --check`. ✅
- **Given** the full quality gate **When** I run all quality checks on the archetype itself **Then** all pass. ✅

## Tasks

- [x] Remove `from __future__ import annotations` from `scripts/build_template.py`
- [x] Remove `from __future__ import annotations` and `TYPE_CHECKING` guard from `scripts/remove_demo.py`; import `Callable` directly from `collections.abc`
- [x] Update `_TEMPLATE_README` Extension Guide to use `CamelCaseModel` + `pydantic.alias_generators.to_camel` instead of custom `_to_camel`
- [x] Remove `from __future__ import annotations` from generated `_POST_GEN_HOOK_CONTENT`
- [x] Fix `UnicodeDecodeError` not caught in `_copy_project_files` (also catch `UnicodeDecodeError` alongside `OSError`)
- [x] Add `_edit_tests_conftest` to `remove_demo.py` to remove dummy service DI shim imports and `_clear_service_caches` fixture
