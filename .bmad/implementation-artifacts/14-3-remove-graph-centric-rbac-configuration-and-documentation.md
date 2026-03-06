# Story 14.3: Remove Graph-Centric RBAC Configuration and Documentation

Status: ready-for-dev

## Story

As a **developer onboarding to the project**,
I want **configuration and docs to reflect token-only inbound RBAC**,
So that **the system is understandable and not misconfigured around removed Graph role lookup behavior**.

## Acceptance Criteria

1. **Given** RBAC-related environment/config surfaces
   **When** this story is complete
   **Then** Graph-role-lookup-specific inbound auth settings are removed
   **And** retained settings clearly describe token-only role enforcement.

2. **Given** auth/RBAC documentation and examples
   **When** reviewed post-change
   **Then** they describe token `roles` as the inbound role source of truth
   **And** they do not describe Graph fallback for inbound authorization.

3. **Given** the codebase references old Graph-centric inbound RBAC behavior
   **When** cleanup is performed
   **Then** stale comments and references are removed
   **And** docs align with actual runtime behavior.

### References

- [Source: .bmad/planning-artifacts/epics/epic-14-token-only-inbound-rbac-with-graph-removal.md]
