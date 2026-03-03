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

## Docker

Build the image:

```bash
docker build -t fastapi-archetype .
```

Run the container (uses SQLite in-memory by default — no `.env` file required):

```bash
docker run -p 8000:8000 fastapi-archetype
```

To pass custom configuration, use `--env-file`:

```bash
docker run --env-file .env -p 8000:8000 fastapi-archetype
```

Swagger UI is available at `http://localhost:8000/docs`.

## Lint and format

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```
