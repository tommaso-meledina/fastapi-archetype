# Story 18.2: Dummy Service Contract, Default and Mock Implementations, and Wiring (v1)

Status: ready-for-dev

## Story

As a **developer**,
I want **the v1 dummies feature to use a service contract with a default (database) and a mock (in-memory) implementation, selected by `profile` via a factory and injected into routes**,
so that **I can run with `PROFILE=mock` and get dummies without a database, and the pattern is established for v1**.

## Acceptance Criteria

1. Contract in `services/contracts/dummy_service.py`: ABC with get_all_dummies(session), get_dummy_by_uuid(session, uuid), create_dummy(session, dummy), update_dummy(session, entity).
2. Default implementation: current v1 logic in `services/v1/implementations/default_dummy_service.py`; metrics and AppException(ErrorCode.DUMMY_NOT_FOUND) preserved.
3. Mock implementation: `services/v1/implementations/mock_dummy_service.py`; same contract; in-memory; list, get by UUID, create, update.
4. Factory in `services/factory.py`: build_dummy_service_v1(settings) returns default or mock by settings.profile.
5. Dependency get_dummy_service_v1 used by v1 routes; routes use Depends(get_dummy_service_v1) and do not import concrete module.
6. AOP logging applied to implementation modules in services/__init__.py.
7. Existing v1 tests pass (override or PROFILE=default as needed).

## Tasks

- [ ] Create contract ABC; default impl; mock impl; factory; dependency; wire routes; AOP; update tests.
