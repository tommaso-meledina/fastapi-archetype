# Story 27.1: Fix `PROJECT_CONTEXT.md` Internal Contradictions

## Status: done

## Story

As a **developer or agent**,
I want **`PROJECT_CONTEXT.md` free of stale references and internal contradictions**,
so that **the authoritative project reference matches the actual codebase**.

## Acceptance Criteria

- **Given** `PROJECT_CONTEXT.md` line 92 **When** I inspect it **Then** it describes the current structlog-based implementation, not the removed `PlainFormatter`, `JsonFormatter`, `SpanFilter` classes. ✅
- **Given** `PROJECT_CONTEXT.md` line 171 **When** I inspect it **Then** it describes DTOs inheriting from `CamelCaseModel` which uses `pydantic.alias_generators.to_camel`. ✅
- **Given** a full-text search of `PROJECT_CONTEXT.md` for `PlainFormatter`, `JsonFormatter`, `SpanFilter`, `_to_camel` (custom function), `AuthFacade`, `AuthProvider` ABC, `DummyServiceV*Contract`, or `implementations/` subdirectory **When** I run it **Then** zero matches are found. ✅
- **Given** any two sections of `PROJECT_CONTEXT.md` describing the same concept **When** I compare them **Then** they are consistent. ✅

## Tasks

- [x] Fix line 92: update `logging.py` project structure comment to describe structlog processor pipeline
- [x] Fix line 171: replace `alias_generator=_to_camel` with `CamelCaseModel`/`pydantic.alias_generators.to_camel`
- [x] Fix line 344: remove `implementations/` subdirectory reference from module organization section
- [x] Fix line 397: replace `logging.config.dictConfig` description with structlog-accurate description
- [x] Fix line 401: replace `SpanFilter` with `_inject_trace_context processor`
