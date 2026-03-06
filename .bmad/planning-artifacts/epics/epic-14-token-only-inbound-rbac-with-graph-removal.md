# Epic 14: Token-Only Inbound RBAC with Graph Removal

Deliver deterministic, fail-closed inbound authorization based solely on Entra token claims (`roles`), while preserving role mapping extensibility and removing all obsolete Graph-based RBAC artifacts so the authorization path is simpler, safer, and easier to maintain.

## Story 14.1: Remove Graph Role Retrieval from Inbound Auth Path

As a **platform maintainer**,
I want **inbound authorization to stop calling Graph for role assignments**,
So that **authorization decisions are deterministic and independent from Graph availability**.

**Acceptance Criteria:**

**Given** an authenticated request to a role-protected endpoint
**When** authorization is evaluated
**Then** no Graph `appRoleAssignments` call is made
**And** role decisions rely only on already-validated token claims and role mapping.

**Given** prior Graph-enrichment code paths in inbound auth
**When** the new strategy is active
**Then** those paths are removed or unreachable
**And** no runtime toggle can re-enable Graph role lookup for inbound auth.

**Given** outbound OAuth features exist for other use cases
**When** this story is implemented
**Then** outbound flows remain available and unchanged
**And** they are not invoked by inbound role checks.

## Story 14.2: Preserve RoleMappingProvider with Token-Claims Resolver

As a **backend engineer**,
I want **to keep the `RoleMappingProvider` abstraction while using token claims as the sole role source**,
So that **internal roles like `admin` still map cleanly without coupling authorization logic to claim literals everywhere**.

**Acceptance Criteria:**

**Given** internal role checks use labels such as `admin`
**When** authorization executes
**Then** the check resolves through `RoleMappingProvider`
**And** mapped external role identifiers are matched against token `roles`.

**Given** a token containing required mapped role(s)
**When** a protected endpoint is requested
**Then** authorization succeeds according to existing policy semantics
**And** no additional external lookup is required.

**Given** token claims are missing or insufficient for required mapped roles
**When** authorization executes
**Then** access is denied (fail closed)
**And** response behavior follows existing unauthorized/forbidden conventions.

## Story 14.3: Remove Graph-Centric RBAC Configuration and Documentation

As a **developer onboarding to the project**,
I want **configuration and docs to reflect token-only inbound RBAC**,
So that **the system is understandable and not misconfigured around removed Graph role lookup behavior**.

**Acceptance Criteria:**

**Given** RBAC-related environment/config surfaces
**When** this story is complete
**Then** Graph-role-lookup-specific inbound auth settings are removed
**And** retained settings clearly describe token-only role enforcement.

**Given** auth/RBAC documentation and examples
**When** reviewed post-change
**Then** they describe token `roles` as the inbound role source of truth
**And** they do not describe Graph fallback for inbound authorization.

**Given** the codebase references old Graph-centric inbound RBAC behavior
**When** cleanup is performed
**Then** stale comments and references are removed
**And** docs align with actual runtime behavior.

## Story 14.4: Validate Token-Only RBAC with Integration Tests

As a **maintainer**,
I want **integration tests that prove token-only role enforcement behavior**,
So that **authorization correctness is protected against regression**.

**Acceptance Criteria:**

**Given** a valid bearer token with required mapped role
**When** calling a role-protected endpoint
**Then** access is granted.

**Given** a valid bearer token missing required role
**When** calling the same endpoint
**Then** access is denied per policy semantics.

**Given** a valid bearer token with no `roles` claim
**When** calling a role-protected endpoint
**Then** access is denied (fail closed).

**Given** the integration suite runs
**When** inspecting authz test paths
**Then** no test relies on Graph role retrieval in inbound authorization
**And** coverage remains adequate for auth/authz behavior.

## Story 14.5: Zombie-Code Eradication for Legacy RBAC Path

As a **technical lead**,
I want **all legacy Graph-based RBAC artifacts removed**,
So that **no dead code, stale tests, or orphaned config remains after replacement**.

**Acceptance Criteria:**

**Given** legacy inbound RBAC implementation artifacts
**When** cleanup is complete
**Then** unused providers/helpers/branches tied to Graph role lookup are removed
**And** there are no dormant fallback stubs left behind.

**Given** test and fixture assets for removed inbound behavior
**When** code is finalized
**Then** obsolete tests/fixtures are deleted or rewritten
**And** surviving tests assert the new token-only behavior.

**Given** quality checks and repository review
**When** the epic implementation is complete
**Then** no references to removed inbound Graph-role strategy remain in active code paths
**And** maintainability NFR (no dead code) is satisfied.
