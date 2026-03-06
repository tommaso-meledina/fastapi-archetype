# Story 14.4: Validate Token-Only RBAC with Integration Tests

Status: ready-for-dev

## Story

As a **maintainer**,
I want **integration tests that prove token-only role enforcement behavior**,
So that **authorization correctness is protected against regression**.

## Acceptance Criteria

1. **Given** a valid bearer token with required mapped role
   **When** calling a role-protected endpoint
   **Then** access is granted.

2. **Given** a valid bearer token missing required role
   **When** calling the same endpoint
   **Then** access is denied per policy semantics.

3. **Given** a valid bearer token with no `roles` claim
   **When** calling a role-protected endpoint
   **Then** access is denied (fail closed).

4. **Given** the integration suite runs
   **When** inspecting authz test paths
   **Then** no test relies on Graph role retrieval in inbound authorization
   **And** coverage remains adequate for auth/authz behavior.

### References

- [Source: .bmad/planning-artifacts/epics/epic-14-token-only-inbound-rbac-with-graph-removal.md]
