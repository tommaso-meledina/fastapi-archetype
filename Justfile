# Task runner for fastapi-archetype
# Usage: just <recipe>   (requires https://github.com/casey/just)

default:
    @just --list

lint:
    uv run ruff check

format:
    uv run ruff format --check

typecheck:
    uv run ty check

test:
    uv run pytest

run:
    uv run uvicorn fastapi_archetype.main:app --reload
