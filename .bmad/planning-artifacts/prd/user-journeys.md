# User Journeys

## Journey 1: SWE Creates a New Python/FastAPI Service (Primary User - Success Path)

**Persona:** Alex, a software engineer tasked with building a new Python/FastAPI microservice for a multi-runtime project. Alex is not a Python specialist but is competent across languages.

**Journey:**

1. **Clone:** Alex clones the fastapi-archetype repository as the starting point for the new service
2. **Explore:** Alex reviews the project structure, reads the docs, and examines how the `/dummies` resource is wired (model, route, tests, AOP, observability)
3. **Verify:** Alex runs the test suite (`pytest`) to confirm all capabilities work together -- tests pass, coverage is >90%
4. **Run:** Alex starts the application locally, hits `/docs` to see Swagger UI, exercises the `GET /dummies` and `POST /dummies` endpoints, checks `/metrics` for Prometheus output
5. **Clean:** Alex runs `python3 scripts/remove_demo.py` to strip all demo boilerplate, leaving a clean project with all infrastructure intact and all remaining tests passing
6. **Adapt:** Alex adds the actual domain (e.g., `Order` model, `/orders` resource), following the structural scaffolding left in place (empty version directories, infrastructure modules) and the patterns documented in the project
7. **Build:** Alex builds the Docker image, verifies it runs, and deploys the new service with confidence that ORM, validation, docs, AOP, observability, and configuration management are all in place

## Journey 2: SWE Encounters a Problem (Primary User - Edge Case)

**Persona:** Alex (same as above), but something goes wrong during adaptation.

**Journey:**

1. Alex replaces the dummy domain but introduces a validation error in the new Pydantic/SQLModel model
2. The test suite catches the issue immediately -- pytest + TestClient surface the exact failure
3. Alex fixes the model, re-runs tests, confirms green
4. Alex verifies that AOP logging still intercepts the new domain's functions and that OTEL/Prometheus instrumentation remains functional after the domain swap

## Journey Requirements Summary

| Journey | Capabilities Revealed |
|---|---|
| Success Path (clone → clean → adapt → deploy) | Clear project structure, demo removal script, documented patterns, structural scaffolding, comprehensive tests, working Dockerfile, Swagger UI, configuration management |
| Edge Case (error during adaptation) | Test coverage catching regressions, AOP working on new domains, observability surviving domain changes |
