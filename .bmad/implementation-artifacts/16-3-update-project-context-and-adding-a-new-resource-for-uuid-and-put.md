# Story 16.3: Update PROJECT_CONTEXT and "Adding a New Resource" for UUID and PUT

Status: done

## Story

As a **developer onboarding to the project**,
I want **PROJECT_CONTEXT and "Adding a New Resource" to describe the entity UUID, DTOs exposing uuid not id, and the PUT-by-UUID pattern with path/body validation**,
so that **new resources can follow the same pattern**.

## Acceptance Criteria

1. **Given** PROJECT_CONTEXT **When** I read the project structure and conventions **Then** they describe that entities may have a `uuid` for client-facing identity **And** that DTOs expose `uuid` and never internal `id` **And** that PUT can use path + body UUID with 400 when they mismatch.
2. **Given** the "Adding a New Resource" instructions **When** they cover update semantics **Then** they include the pattern: UUID on entity, UUID in DTOs, PUT with path and body UUID and validation for match.

## Tasks / Subtasks

- [x] Task 1 (AC: #1) — PROJECT_CONTEXT describes UUID and PUT
  - [x] Ensure Data Persistence (or equivalent) describes entity uuid, DTOs expose uuid not id, PUT path+body UUID and 400 on mismatch.
  - [x] Ensure REST API / endpoints table lists PUT where applicable (e.g. PUT /v1/dummies/{uuid}).
- [x] Task 2 (AC: #2) — "Adding a New Resource" includes UUID and PUT pattern
  - [x] Ensure steps for entity (uuid when needed), DTOs (uuid not id), and update semantics (PUT path+body UUID, validate match) are present.

## Dev Notes

- PROJECT_CONTEXT already contains §2 Data Persistence "Client identity (UUID vs ID)" and "Adding a New Resource" with UUID and PUT in steps 1, 2, 7. Verify and add any missing piece (e.g. PUT in endpoints table).

## Dev Agent Record

### Completion Notes List

- PROJECT_CONTEXT already described UUID and PUT in §2 Data Persistence and "Adding a New Resource"; added PUT /v1/dummies/{uuid} to the REST API endpoints table.

### File List

- PROJECT_CONTEXT.md (modified)
