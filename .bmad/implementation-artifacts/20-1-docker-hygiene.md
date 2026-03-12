# Story 20.1: Docker Hygiene

**Epic:** 20 — Hygiene & Quick Wins
**Status:** in-progress

## Story

As a **developer or operator**,
I want **the Dockerfile to set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` and support configurable uvicorn workers**,
so that **container behaviour is predictable and logs are not lost on crashes**.

## Acceptance Criteria

- **Given** the `Dockerfile` **When** I inspect environment variables **Then** `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` are set.
- **Given** the `Dockerfile` **When** I inspect the uvicorn command **Then** the worker count is configurable via an environment variable (`WEB_CONCURRENCY`) with a sensible default (`1`).
- **Given** a built Docker image **When** I run it **Then** no `.pyc` files are created inside the container **And** stdout/stderr are unbuffered.

## Tasks

- [x] Add `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` to the runtime stage `ENV` block in `Dockerfile`
- [x] Change `CMD` to use `WEB_CONCURRENCY` env var for worker count (default `1`)
