# Epic 4: Comprehensive Test Suite

A developer can run the complete test suite to verify all capabilities work together. Unit tests mock externals, integration tests use SQLite in-memory, and the suite achieves >90% code coverage.

## Story 4.1: Test Infrastructure and Configuration

As a **software engineer**,
I want **a pytest test infrastructure with SQLite in-memory database override and shared fixtures**,
So that **tests run without external dependencies and I have a clear pattern for writing new tests against any resource**.

**Acceptance Criteria:**

**Given** `tests/conftest.py` exists
**When** I inspect its contents
**Then** it creates a SQLite in-memory SQLAlchemy engine
**And** it overrides the application's database session dependency with the SQLite session
**And** it provides a FastAPI `TestClient` fixture for HTTP request testing
**And** `SQLModel.metadata.create_all` is called against the test engine to set up tables

**Given** pytest is configured in `pyproject.toml`
**When** I run `uv run pytest`
**Then** pytest discovers and executes tests from the `tests/` directory
**And** no external infrastructure (MariaDB, OTEL collector, etc.) is required

**Given** the test fixtures
**When** a test function requests the test client fixture
**Then** each test gets an isolated database state
**And** the application's dependency injection is overridden to use the SQLite test database

## Story 4.2: Endpoint and Service Test Coverage

As a **software engineer**,
I want **comprehensive tests covering all endpoints with valid and invalid inputs, service logic with mocked dependencies, and error handling paths**,
So that **I can verify all capabilities work together and the test patterns serve as a template for testing new resources**.

**Acceptance Criteria:**

**Given** `tests/api/test_dummy_routes.py` exists
**When** I run the endpoint tests
**Then** `GET /dummies` is tested for empty and populated responses
**And** `POST /dummies` is tested with valid input returning 201
**And** `POST /dummies` is tested with invalid input returning the structured error response
**And** all response payloads are verified for camelCase JSON field names

**Given** `tests/services/test_dummy_service.py` exists
**When** I run the service tests
**Then** service functions are tested in isolation with mocked database sessions
**And** both success and error paths are covered

**Given** `tests/core/test_config.py` exists
**When** I run the configuration tests
**Then** valid configuration loading is tested
**And** missing required values trigger a validation error

**Given** `tests/core/test_errors.py` exists
**When** I run the error handling tests
**Then** `AppException` produces the correct structured error response format
**And** the global exception handler is tested

**Given** `tests/aop/test_logging_decorator.py` exists
**When** I run the AOP tests
**Then** the decorator correctly logs function inputs and return values
**And** `apply_logging` correctly wraps all public functions in a module

**Given** the full test suite
**When** I run `uv run pytest --cov`
**Then** code coverage exceeds 90%
**And** all tests pass
