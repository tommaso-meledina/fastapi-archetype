# Epic 5: Production-Ready Containerization

A developer can build a Docker image and run the full application in a container with no configuration beyond the `.env` file. The image runs consistently across Linux and macOS.

## Story 5.1: Multi-Stage Dockerfile

As a **software engineer**,
I want **a multi-stage Dockerfile that builds a production-ready container image using `python:3.14-slim`**,
So that **I can build and run the application in a container with no configuration beyond the `.env` file, and the image works consistently across Linux and macOS**.

**Acceptance Criteria:**

**Given** `Dockerfile` exists at the project root
**When** I inspect its contents
**Then** it uses a multi-stage build: a build stage that installs dependencies and a runtime stage that copies only what's needed
**And** the runtime base image is `python:3.14-slim`
**And** no build tools, caches, or source-only files are present in the final image

**Given** a valid `.env` file exists
**When** I run `docker build -t fastapi-archetype .`
**Then** the image builds successfully with no errors

**Given** the built Docker image
**When** I run `docker run --env-file .env -p 8000:8000 fastapi-archetype`
**Then** the application starts and serves requests on port 8000
**And** Swagger UI is accessible at `http://localhost:8000/docs`
**And** no additional configuration beyond the `.env` file is required

**Given** the Docker image
**When** I run it on Linux and macOS
**Then** the application behaves identically on both platforms without modification

**Given** the Docker image
**When** I inspect its contents
**Then** it has no host-specific dependencies beyond what is declared in `pyproject.toml`
**And** the image uses uv for dependency installation in the build stage
