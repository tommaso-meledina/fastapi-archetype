# Epic Request: Entra Authorization Strategy Simplification

## Context

Current implementation enriches user roles through Microsoft Graph (`/users/{id}/appRoleAssignments`) using OBO token exchange during authorization checks.

Recent investigation against official Microsoft Entra documentation indicates this is valid, but not the simplest default for API authorization in our scenario.

## Problem Statement

Per-request Graph role lookup adds complexity and operational risk:

- extra network dependency in auth path
- additional Entra/Graph permission and consent requirements
- higher latency and more failure modes in authorization

## Documentation Findings (Microsoft Learn)

1. Preferred pattern for API authorization is app roles in access tokens and direct `roles` claim evaluation:
   - https://learn.microsoft.com/en-us/security/zero-trust/develop/configure-tokens-group-claims-app-roles
2. Graph appRoleAssignments API is available for role retrieval, but is an explicit extra call:
   - https://learn.microsoft.com/en-us/graph/api/user-list-approleassignments?view=graph-rest-1.0
3. Token optional claims / claim-shaping considerations:
   - https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference

## Proposed Epic Goal

Define and implement a simpler authorization strategy where:

- `roles` claim in Entra access token is the primary source of truth
- Graph fallback is used only when strictly needed (for example overage/edge cases or explicit real-time directory requirements)

## Expected Scope for PM Epic

1. Product/architecture decision on role source strategy (token-first vs Graph-first vs hybrid fallback).
2. Configuration strategy and migration plan from current Graph-centric enforcement.
3. Security and operational constraints (least privilege, failure behavior, observability).
4. Story breakdown for implementation, testing, rollout, and backward compatibility.
5. Success criteria and measurable outcomes (latency, reliability, auth correctness).

## Notes from Debug Session

- Token validation issue was traced to issuer mismatch (`v1` token issuer vs configured `v2` issuer).
- Logging was rolled back to safe defaults after debugging.
- Security hardening retained in Entra provider:
  - enforce `RS256`
  - fail when token `kid` is present but no JWKS key matches
  - validate signing key metadata (`kty`/`use`)

