# Starter Template Evaluation

## Primary Technology Domain

API backend (Python 3.14 / FastAPI) — technology stack fully specified by PRD as this is a reference implementation.

## Starter Options Considered

| Option | Verdict | Rationale |
|---|---|---|
| uvicorn-poetry-fastapi-project-template | Rejected | Poetry-based; pre-wired Docker/Uvicorn but missing SQLModel, OTEL, Prometheus |
| fastapi-modular-boilerplate | Rejected | Over-scoped (async SQLAlchemy, Alembic, JWT, GitHub Actions); heavy pruning defeats the purpose |
| FastLaunchAPI-style enterprise templates | Rejected | SaaS-oriented (Celery, Stripe, OAuth2); fundamentally different use case |
| `uv init` (clean init) | **Selected** | Full control over every dependency and structural decision; aligns with reference implementation purpose |

## Selected Starter: uv Clean Init

**Rationale for Selection:**

This project IS the reference implementation — its value lies in demonstrating how 12 capabilities integrate from scratch. Using an opinionated third-party template would import unwanted patterns, require pruning, and undermine the project's purpose as a proven-from-zero archetype. A clean uv init ensures every dependency is intentional and every structural decision is documented.

**Initialization Command:**

```bash
uv init fastapi-archetype
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- Python 3.14 (specified via `pyproject.toml` `requires-python` and managed by `uv python pin`)

**Build Tooling:**
- uv for dependency management, virtual environment, and reproducible builds via cross-platform `uv.lock`
- `pyproject.toml` as single project configuration file

**Testing Framework:**
- pytest (added as dev dependency via `uv add --dev pytest`)

**Code Organization:**
- Project root with `pyproject.toml`, `uv.lock`, and source package
- `tests/` directory at project root

**Development Experience:**
- `uv run` for command execution within the managed environment
- `uv add` / `uv remove` for dependency management with automatic lockfile updates
- `uv sync` for reproducible environment setup from lockfile

**Note:** Project initialization using this command should be the first implementation story.
