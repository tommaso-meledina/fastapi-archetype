# oauth2-spring-security parity targets

This document captures which behaviors from `oauth2-spring-security` we mirror and which
sharp edges we intentionally avoid in this FastAPI implementation.

## In-scope parity targets

- Resource-server style bearer-token authentication with JWT validation.
- Issuer validation and optional audience validation.
- Token claim mapping into a typed principal model (`sub`, `oid`, `name`, `scp`, `appid`,
  `roles`, `groups` for Entra-style claims).
- Outbound token acquisition:
  - `client_credentials`
  - `urn:ietf:params:oauth:grant-type:jwt-bearer` (OBO)
- Graph-backed app role retrieval for current user and arbitrary user id.

## Deliberate non-goals

- No opaque-token introspection flow.
- No built-in multi-IdP implementation in phase one (provider contract is ready for it).
- No local auth/token issuer flow. Auth is either disabled (`AUTH_TYPE=none`) or external IdP (`AUTH_TYPE=entra`).

## Sharp edges we avoid compared to the Spring library

- No implicit open fallback for non-matching routes.
  - Protection is explicit and per-route via FastAPI dependencies.
- No global mutable security context access pattern.
  - Principal is resolved request-scoped and injected with `Depends`.
- No blocking external calls in request paths.
  - Outbound OAuth/Graph calls are async.
- No inconsistent role return shape.
  - App-role APIs normalize to a consistent internal list of role identifiers.
