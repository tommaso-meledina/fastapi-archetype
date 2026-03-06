# Story 14.1: Remove Graph Role Retrieval from Inbound Auth Path

Status: ready-for-dev

## Story

As a **platform maintainer**,
I want **inbound authorization to stop calling Graph for role assignments**,
So that **authorization decisions are deterministic and independent from Graph availability**.

## Acceptance Criteria

1. **Given** an authenticated request to a role-protected endpoint
   **When** authorization is evaluated
   **Then** no Graph `appRoleAssignments` call is made
   **And** role decisions rely only on already-validated token claims and role mapping.

2. **Given** prior Graph-enrichment code paths in inbound auth
   **When** the new strategy is active
   **Then** those paths are removed or unreachable
   **And** no runtime toggle can re-enable Graph role lookup for inbound auth.

3. **Given** outbound OAuth features exist for other use cases
   **When** this story is implemented
   **Then** outbound flows remain available and unchanged
   **And** they are not invoked by inbound role checks.

### References

- [Source: .bmad/planning-artifacts/epics/epic-14-token-only-inbound-rbac-with-graph-removal.md]
