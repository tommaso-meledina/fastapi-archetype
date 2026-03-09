# Story 18.3: Apply Profile and Service Contract Pattern to v2 Dummies

Status: done

## Story

As a **developer**, I want **the v2 dummies feature to use the same profile-driven contract pattern (contract, default impl, mock impl, factory, DI)**, so that **v2 dummies also switch by `PROFILE` and the pattern is consistent across versions**.

## Acceptance Criteria

- v2 dummy service contract (get_all_dummies, create_dummy); default and mock implementations; factory; v2 routes depend on dependency; PROFILE=mock works for GET/POST /v2/dummies; all v2 tests pass.
