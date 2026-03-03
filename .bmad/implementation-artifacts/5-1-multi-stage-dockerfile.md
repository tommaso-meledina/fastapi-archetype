# Story 5.1: Multi-Stage Dockerfile

Status: done

## Story

As a **software engineer**,
I want **a multi-stage Dockerfile that builds a production-ready container image using `python:3.14-slim`**,
so that **I can build and run the application in a container with no configuration beyond the `.env` file, and the image works consistently across Linux and macOS**.

## Acceptance Criteria

1. **Given** `Dockerfile` exists at the project root **When** I inspect its contents **Then** it uses a multi-stage build: a build stage that installs dependencies and a runtime stage that copies only what's needed **And** the runtime base image is `python:3.14-slim` **And** no build tools, caches, or source-only files are present in the final image.
2. **Given** a valid `.env` file exists **When** I run `docker build -t fastapi-archetype .` **Then** the image builds successfully with no errors.
3. **Given** the built Docker image **When** I run `docker run --env-file .env -p 8000:8000 fastapi-archetype` **Then** the application starts and serves requests on port 8000 **And** Swagger UI is accessible at `http://localhost:8000/docs` **And** no additional configuration beyond the `.env` file is required.
4. **Given** the Docker image **When** I run it on Linux and macOS **Then** the application behaves identically on both platforms without modification.
5. **Given** the Docker image **When** I inspect its contents **Then** it has no host-specific dependencies beyond what is declared in `pyproject.toml` **And** the image uses uv for dependency installation in the build stage.

## Tasks / Subtasks

- [x] Task 1: Create `.dockerignore` file (AC: 1, 5)
  - [x] Exclude `.git/`, `__pycache__/`, `.venv/`, `.env`, `*.pyc`, `.ruff_cache/`, `.bmad/`, `_bmad/`, `tests/`, `docs/`, `.pytest_cache/`, `.coverage`
- [x] Task 2: Create multi-stage `Dockerfile` (AC: 1, 2, 5)
  - [x] Build stage: use `python:3.14-slim` as builder, install `uv`, copy `pyproject.toml` + `uv.lock`, install production dependencies only (no dev group)
  - [x] Runtime stage: use `python:3.14-slim`, copy installed virtual environment and source code from builder, set `PYTHONPATH`, expose port 8000
  - [x] Use non-root user in runtime stage
  - [x] CMD runs `uvicorn fastapi_archetype.main:app --host 0.0.0.0 --port 8000`
- [x] Task 3: Verify image builds and runs (AC: 2, 3, 4)
  - [x] `docker build -t fastapi-archetype .` completes without errors
  - [x] `docker run --env-file .env -p 8000:8000 fastapi-archetype` starts the app
  - [x] `http://localhost:8000/docs` serves Swagger UI (returns 200)
- [x] Task 4: Verify final image cleanliness (AC: 1, 5)
  - [x] No build tools (uv, pip, setuptools) in the final image — uv absent; pip is from base python:3.14-slim only
  - [x] No project test files or documentation in the final image — /app/ contains only .venv
  - [x] Image size: 307MB (reasonable for python:3.14-slim + production dependencies)
- [x] Task 5: Update README with Docker usage instructions (AC: 3)
  - [x] Add build and run commands to README.md
- [x] Task 6: Run quality checks
  - [x] `uv run ruff check src/ tests/` passes
  - [x] `uv run ruff format --check src/ tests/` passes
  - [x] `uv run pytest` — 38 tests pass, no regressions

## Dev Notes

### Architecture Compliance

- ASGI server: Uvicorn standalone 0.41.0 [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Infrastructure & Deployment]
- Container: Multi-stage Dockerfile, `python:3.14-slim` runtime [Source: same]
- Dependency management: uv, `pyproject.toml` + `uv.lock` for reproducibility [Source: same]
- Build system: `uv_build` [Source: pyproject.toml]
- Default DB: SQLite in-memory (`DB_DRIVER=sqlite`) — no external services needed for container startup

### Key Implementation Details

- App entry point: `fastapi_archetype.main:app` (ASGI application object)
- Project uses `src/` layout: source lives in `src/fastapi_archetype/`
- `.python-version` contains `3.14`
- `uv.lock` exists at project root for reproducible installs
- `.env.example` documents all configuration variables
- Configuration loads from `.env` via pydantic-settings `BaseSettings` with `env_file=".env"`
- The `--env-file .env` flag in `docker run` passes environment variables to the container; pydantic-settings will read them from the process environment (NOT from a file inside the container)

### uv in Docker

- Install uv in build stage via the official standalone installer or `pip install uv`
- Use `uv sync --frozen --no-dev` to install only production dependencies from the lockfile
- uv creates a `.venv` directory; copy that to the runtime stage
- Do NOT copy uv itself to the runtime stage

### File Structure

```
Dockerfile          (new — project root)
.dockerignore       (new — project root)
README.md           (modified — add Docker section)
```

### Previous Story Intelligence

- Story 4.2 (most recent): 37 tests, 95% coverage, all passing. Quality checks pass.
- All 4 epics complete with passing tests and lint. No regressions to worry about.
- Test infrastructure uses SQLite in-memory with `StaticPool` via conftest fixtures.

### References

- [Source: .bmad/planning-artifacts/epics/epic-5-production-ready-containerization.md]
- [Source: .bmad/planning-artifacts/architecture/core-architectural-decisions.md#Infrastructure & Deployment]

## Senior Developer Review (AI)

**Review Date:** 2026-03-03
**Review Outcome:** Approve (with minor fixes applied)

**Findings:** 0 High, 1 Medium, 3 Low

**Action Items:**
- [x] [MEDIUM] Pin uv Docker image version from `:latest` to `:0.10.7` for reproducible builds
- [x] [LOW] Improve README Docker section to clarify `.env` is optional (SQLite defaults work without it)
- [ ] [LOW] Consider adding HEALTHCHECK instruction for container orchestrator support
- [ ] [LOW] Consider excluding IDE directories (`.cursor/`) from `.dockerignore` build context

**All ACs validated and implemented. All tasks confirmed complete.**

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent)

### Debug Log References

### Completion Notes List

- Created `.dockerignore` excluding dev/build artifacts, tests, docs, bmad directories
- Created multi-stage `Dockerfile`: build stage uses `python:3.14-slim` + uv (via distroless image copy), installs production deps with `uv sync --locked --no-dev --no-editable`; runtime stage copies only `.venv`, runs as non-root `app` user
- Docker image builds successfully (307MB), container starts and serves Swagger UI at `/docs` (HTTP 200), API responds at `/dummies`
- Final image has no uv, no project source outside venv, no test files
- Updated README.md with Docker build/run instructions
- All 38 existing tests pass, lint and format checks clean

### Change Log

- 2026-03-03: Implemented multi-stage Dockerfile for production-ready containerization (Story 5.1)
- 2026-03-03: Code review — pinned uv version to 0.10.7, improved README Docker docs

### File List

- Dockerfile (created)
- .dockerignore (created)
- README.md (modified — added Docker section)
