# fastapi-archetype

## Purpose

A reference FastAPI application demonstrating how enterprise-grade cross-cutting concerns — ORM, configuration management, structured error handling, AOP logging, OpenTelemetry tracing, Prometheus metrics, and containerization — integrate coherently in a single Python 3.14 project. Designed as a copy-and-adapt template for new microservices.

## Usage

Install dependencies:

```bash
uv sync
```

Run the application (uses SQLite in-memory by default — no database setup needed):

```bash
uv run uvicorn fastapi_archetype.main:app --reload
```

To use MariaDB instead, set `DB_DRIVER=mysql+pymysql` in a `.env` file (see `.env.example`).

Lint and format:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```
