# Story 14.2: Preserve RoleMappingProvider with Token-Claims Resolver

Status: ready-for-dev

## Story

As a **backend engineer**,
I want **to keep the `RoleMappingProvider` abstraction while using token claims as the sole role source**,
So that **internal roles like `admin` still map cleanly without coupling authorization logic to claim literals everywhere**.

## Acceptance Criteria

1. **Given** internal role checks use labels such as `admin`
   **When** authorization executes
   **Then** the check resolves through `RoleMappingProvider`
   **And** mapped external role identifiers are matched against token `roles`.

2. **Given** a token containing required mapped role(s)
   **When** a protected endpoint is requested
   **Then** authorization succeeds according to existing policy semantics
   **And** no additional external lookup is required.

3. **Given** token claims are missing or insufficient for required mapped roles
   **When** authorization executes
   **Then** access is denied (fail closed)
   **And** response behavior follows existing unauthorized/forbidden conventions.

### References

- [Source: .bmad/planning-artifacts/epics/epic-14-token-only-inbound-rbac-with-graph-removal.md]
