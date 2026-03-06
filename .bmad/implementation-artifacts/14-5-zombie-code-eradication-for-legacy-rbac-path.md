# Story 14.5: Zombie-Code Eradication for Legacy RBAC Path

Status: ready-for-dev

## Story

As a **technical lead**,
I want **all legacy Graph-based RBAC artifacts removed**,
So that **no dead code, stale tests, or orphaned config remains after replacement**.

## Acceptance Criteria

1. **Given** legacy inbound RBAC implementation artifacts
   **When** cleanup is complete
   **Then** unused providers/helpers/branches tied to Graph role lookup are removed
   **And** there are no dormant fallback stubs left behind.

2. **Given** test and fixture assets for removed inbound behavior
   **When** code is finalized
   **Then** obsolete tests/fixtures are deleted or rewritten
   **And** surviving tests assert the new token-only behavior.

3. **Given** quality checks and repository review
   **When** the epic implementation is complete
   **Then** no references to removed inbound Graph-role strategy remain in active code paths
   **And** maintainability NFR (no dead code) is satisfied.

### References

- [Source: .bmad/planning-artifacts/epics/epic-14-token-only-inbound-rbac-with-graph-removal.md]
