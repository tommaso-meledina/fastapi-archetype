#!/usr/bin/env python3
"""Build a Cookiecutter template from the fastapi-archetype reference implementation.

Run from the project root:
    python3 scripts/build_template.py -o /path/to/output

Requires only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEMPLATE_DIR_NAME = "{{cookiecutter.project_slug}}"
PACKAGE_DIR_NAME = "{{cookiecutter.package_name}}"

COOKIECUTTER_JSON = {
    "project_name": "My FastAPI Service",
    "project_slug": (
        "{{ cookiecutter.project_name | lower | replace(' ', '-')"
        " | replace('_', '-') }}"
    ),
    "package_name": "{{ cookiecutter.project_slug | replace('-', '_') }}",
    "description": "A FastAPI microservice",
    "author_name": "Your Name",
    "author_email": "you@example.com",
    "include_demo_resource": ["true", "false"],
}

# Paths relative to PROJECT_ROOT that are excluded from the template entirely.
# Directories MUST end with "/".
EXCLUDED_PATHS: set[str] = {
    "_bmad/",
    ".bmad/",
    ".cursor/",
    ".idea/",
    ".git/",
    ".venv/",
    ".coverage",
    ".pytest_cache/",
    ".ruff_cache/",
    "compose/observability/grafana/storage/",
    "INITIAL_CONTEXT.md",
    "ARCH_DECISIONS.md",
    "RELEASE_NOTES.md",
    "PROJECT_CONTEXT.md",
    "AGENTS.md",
    "CLAUDE.md",
    "node-autochglog.config.json",
    ".githooks/",
    "uv.lock",
    ".env",
    "README.md",
    "scripts/build_template.py",
}

# Ordered list of (find, replace) pairs applied to file contents.
# Order matters: specific/longer matches first to avoid partial replacements.
TEXT_REPLACEMENTS: list[tuple[str, str]] = [
    (
        "FASTAPI_ARCHETYPE_CONTEXT_PATH",
        "APP_CONTEXT_PATH",
    ),
    (
        "FASTAPI_ARCHETYPE_DOCKERFILE_PATH",
        "APP_DOCKERFILE_PATH",
    ),
    (
        "tommaso-meledina@users.noreply.github.com",
        "{{cookiecutter.author_email}}",
    ),
    (
        "Tommaso",
        "{{cookiecutter.author_name}}",
    ),
    (
        "A reference FastAPI application demonstrating enterprise patterns",
        "{{cookiecutter.description}}",
    ),
    (
        "fastapi_archetype",
        "{{cookiecutter.package_name}}",
    ),
    (
        "fastapi-archetype",
        "{{cookiecutter.project_slug}}",
    ),
]

BINARY_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pyc",
        ".pyo",
        ".so",
        ".dylib",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".wasm",
        ".map",
    }
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Cookiecutter template from fastapi-archetype.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Output directory for the Cookiecutter template.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output directory if it already exists.",
    )
    return parser.parse_args()


def _is_excluded(rel_path: Path) -> bool:
    rel_str = str(rel_path)
    for excl in EXCLUDED_PATHS:
        if excl.endswith("/"):
            if rel_str == excl.rstrip("/") or rel_str.startswith(excl):
                return True
        elif rel_str == excl:
            return True
    return False


def _is_binary(path: Path) -> bool:
    return path.suffix.lower() in BINARY_EXTENSIONS


def _apply_replacements(content: str) -> str:
    for find, replace in TEXT_REPLACEMENTS:
        content = content.replace(find, replace)
    return content


def _compute_dest_path(rel_path: Path) -> Path:
    parts = list(rel_path.parts)
    if len(parts) >= 2 and parts[0] == "src" and parts[1] == "fastapi_archetype":
        parts[1] = PACKAGE_DIR_NAME
    return Path(*parts)


def _collect_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(PROJECT_ROOT)
        if _is_excluded(rel):
            continue
        files.append(rel)
    return files


def _write_cookiecutter_json(output_dir: Path) -> None:
    dest = output_dir / "cookiecutter.json"
    dest.write_text(
        json.dumps(COOKIECUTTER_JSON, indent=4) + "\n",
        encoding="utf-8",
    )


def _write_post_gen_hook(output_dir: Path) -> None:
    hooks_dir = output_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "post_gen_project.py"
    hook_path.write_text(_POST_GEN_HOOK_CONTENT, encoding="utf-8")


_POST_GEN_HOOK_CONTENT = r'''#!/usr/bin/env python3
"""Cookiecutter post-generation hook.

Removes demo (Dummy CRUD) boilerplate when include_demo_resource is false.
"""
from __future__ import annotations

import sys
from pathlib import Path

INCLUDE_DEMO = "{{ cookiecutter.include_demo_resource }}" == "true"
PACKAGE_NAME = "{{ cookiecutter.package_name }}"

PROJECT_ROOT = Path.cwd()

FILES_TO_DELETE = [
    f"src/{PACKAGE_NAME}/models/dummy.py",
    f"src/{PACKAGE_NAME}/api/v1/dummy_routes.py",
    f"src/{PACKAGE_NAME}/api/v2/dummy_routes.py",
    f"src/{PACKAGE_NAME}/services/v1/dummy_service.py",
    f"src/{PACKAGE_NAME}/services/v2/dummy_service.py",
    "tests/api/test_dummy_routes.py",
    "tests/api/test_v2_dummy_routes.py",
    "tests/services/v1/test_dummy_service.py",
    "tests/services/v2/test_dummy_service.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _collapse_blank_lines(text: str) -> str:
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    return text


def _edit_constants(path: Path) -> None:
    content = _read(path)
    block = (
        "\n\n"
        "DUMMIES = ResourceDefinition(\n"
        '    path="/dummies",\n'
        '    name="Dummies",\n'
        '    description="Dummy resources for demonstrating CRUD patterns",\n'
        ")\n"
    )
    content = content.replace(block, "")
    _write(path, _collapse_blank_lines(content))


def _edit_errors(path: Path) -> None:
    content = _read(path)
    content = content.replace(
        '    DUMMY_NOT_FOUND = ("DUMMY_NOT_FOUND", "Dummy not found", 404)\n', ""
    )
    _write(path, content)


def _edit_config(path: Path) -> None:
    content = _read(path)
    content = content.replace(
        '    rate_limit_get_dummies: str = "100/minute"\n'
        '    rate_limit_post_dummies: str = "10/minute"\n\n',
        "",
    )
    _write(path, content)


def _edit_services_init(path: Path) -> None:
    _write(path, "")


def _edit_api_v1_init(path: Path) -> None:
    content = (
        "from __future__ import annotations\n"
        "\n"
        "from fastapi import APIRouter\n"
        "\n"
        'router = APIRouter(prefix="/v1")\n'
    )
    _write(path, content)


def _edit_api_v2_init(path: Path) -> None:
    content = (
        "from __future__ import annotations\n"
        "\n"
        "from fastapi import APIRouter\n"
        "\n"
        'router = APIRouter(prefix="/v2")\n'
    )
    _write(path, content)


def _edit_prometheus(path: Path) -> None:
    content = _read(path)
    content = content.replace(
        "from dataclasses import dataclass\n", ""
    )
    content = content.replace(
        "from prometheus_client import Counter\n", ""
    )
    block = (
        "\n\n"
        "@dataclass(frozen=True)\n"
        "class Counters:\n"
        "    dummies_created_total: Counter\n"
        "\n\n"
        "@dataclass(frozen=True)\n"
        "class Metrics:\n"
        "    counters: Counters\n"
        "\n\n"
        "metrics = Metrics(\n"
        "    counters=Counters(\n"
        "        dummies_created_total=Counter(\n"
        '            "dummies_created_total",\n'
        '            "Total number of dummy resources created",\n'
        '            labelnames=["api_version"],\n'
        "        ),\n"
        "    ),\n"
        ")\n"
    )
    content = content.replace(block, "")
    _write(path, _collapse_blank_lines(content))


def _edit_env_example(path: Path) -> None:
    content = _read(path)
    lines = content.splitlines(keepends=True)
    lines = [
        line
        for line in lines
        if "RATE_LIMIT_GET_DUMMIES" not in line
        and "RATE_LIMIT_POST_DUMMIES" not in line
    ]
    _write(path, "".join(lines))


def main() -> int:
    if INCLUDE_DEMO:
        return 0

    print("Removing Dummy CRUD demo boilerplate...")

    for rel_path in FILES_TO_DELETE:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            full_path.unlink()
            print(f"  Deleted: {rel_path}")

    edit_dispatch: list[tuple[str, object]] = [
        (f"src/{PACKAGE_NAME}/core/constants.py", _edit_constants),
        (f"src/{PACKAGE_NAME}/core/errors.py", _edit_errors),
        (f"src/{PACKAGE_NAME}/core/config.py", _edit_config),
        (f"src/{PACKAGE_NAME}/services/__init__.py", _edit_services_init),
        (f"src/{PACKAGE_NAME}/api/v1/__init__.py", _edit_api_v1_init),
        (f"src/{PACKAGE_NAME}/api/v2/__init__.py", _edit_api_v2_init),
        (f"src/{PACKAGE_NAME}/observability/prometheus.py", _edit_prometheus),
        (".env.example", _edit_env_example),
    ]

    for rel_path, edit_fn in edit_dispatch:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            edit_fn(full_path)
            print(f"  Edited:  {rel_path}")

    print("\nDemo boilerplate removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


_TEMPLATE_README = (  # noqa: E501
    r"""# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Usage

### Using `uv`

Install dependencies:

```bash
uv sync
```

Run the application (SQLite in-memory by default):

```bash
uv run uvicorn {{cookiecutter.package_name}}.main:app --reload
```

Set `DB_DRIVER=mysql+pymysql` in `.env` for MariaDB (see `.env.example`).

### Using Docker

```bash
docker build -t {{cookiecutter.project_slug}} .
docker run -p 8000:8000 {{cookiecutter.project_slug}}
```

With custom configuration:

```bash
docker run --env-file .env -p 8000:8000 {{cookiecutter.project_slug}}
```

### Using Docker Compose

```bash
docker compose -f compose/docker-compose.yaml up --build
```

Starts the application with MariaDB and the observability stack.

| Service | Port | Purpose |
|---------|------|---------|
| Application | 8000 | FastAPI (connected to MariaDB) |
| MariaDB | 3306 | Persistent database |
| OTEL Collector | 4317 | Receives OTLP traces |
| Jaeger | 16686 | Trace visualization |
| Prometheus | 9090 | Metrics scraping |
| Grafana | 3001 | Dashboards |

## Capabilities

Integrated enterprise capabilities, working together out of the box:

- **REST API** with CRUD and OpenAPI docs at `/docs`, `/redoc`
- **SQLModel ORM** (SQLite in-memory or MariaDB)
- **Configuration** via pydantic-settings with `.env` support
- **Structured errors** with enum codes and JSON responses
- **API versioning** (`/v1`, `/v2`) with `APIRouter`
- **AOP function logging** at the module level
- **OpenTelemetry tracing** with optional OTLP export
- **Prometheus metrics** (HTTP + custom counters) at `/metrics`
- **Rate limiting** per endpoint, configurable via env vars
- **Auth and RBAC** with external IdP bearer-token validation
- **Containerization** via multi-stage Dockerfile
- **pytest suite** with >90% coverage (SQLite in-memory)
- **Code quality** via Ruff (Python 3.14)

## Testing

```bash
uv run pytest
uv run pytest --cov={{cookiecutter.package_name}} --cov-report=term-missing
```

## Code Quality

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

{% if cookiecutter.include_demo_resource == 'true' -%}
## Demo Resource

This project includes a `/dummies` CRUD resource as a working
example. Run the removal script when ready to add your own domain:

```bash
python3 scripts/remove_demo.py
```

This strips demo files and edits shared modules, leaving
infrastructure intact and all remaining tests passing.

{% endif -%}
## Extension Guide

To add a new resource (e.g. `Widget`):

**1. Model** — `src/{{cookiecutter.package_name}}/models/widget.py`:

```python
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

def _to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

class Widget(SQLModel, table=True):
    model_config = ConfigDict(
        alias_generator=_to_camel, populate_by_name=True,
    )
    __tablename__ = "WIDGET"
    id: int | None = Field(default=None, primary_key=True)
    label: str
    weight: float | None = None
```

**2. Constant** — `core/constants.py`:

```python
WIDGETS = ResourceDefinition(
    path="/widgets",
    name="Widgets",
    description="Widget resources",
)
```

**3. Service** — `services/v1/widget_service.py`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlmodel import select
from {{cookiecutter.package_name}}.models.widget import Widget

if TYPE_CHECKING:
    from sqlmodel import Session

def get_all_widgets(session: Session) -> list[Widget]:
    return list(session.exec(select(Widget)).all())

def create_widget(session: Session, widget: Widget) -> Widget:
    session.add(widget)
    session.commit()
    session.refresh(widget)
    return widget
```

**4. AOP logging** — `services/__init__.py`:

```python
from {{cookiecutter.package_name}}.services.v1 import (
    widget_service as v1_widget_service,
)
apply_logging(v1_widget_service)
```

**5. Routes** — `api/v1/widget_routes.py`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, Request, Response, status
from {{cookiecutter.package_name}}.core.constants import WIDGETS
from {{cookiecutter.package_name}}.core.database import get_session
from {{cookiecutter.package_name}}.core.rate_limit import limiter
from {{cookiecutter.package_name}}.core.config import AppSettings
from {{cookiecutter.package_name}}.models.widget import Widget
from {{cookiecutter.package_name}}.services.v1 import widget_service

if TYPE_CHECKING:
    from sqlmodel import Session

router = APIRouter(prefix=WIDGETS.path, tags=[WIDGETS.name])
_settings = AppSettings()

@router.get("", response_model=list[Widget])
@limiter.limit(_settings.rate_limit_get_widgets)
def list_widgets(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> list[Widget]:
    return widget_service.get_all_widgets(session)

@router.post(
    "", response_model=Widget,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(_settings.rate_limit_post_widgets)
def create_widget(
    request: Request,
    widget: Widget,
    response: Response,
    session: Session = Depends(get_session),
) -> Widget:
    return widget_service.create_widget(session, widget)
```

**6. Register router** — `api/v1/__init__.py`:

```python
from {{cookiecutter.package_name}}.api.v1.widget_routes import (
    router as widget_router,
)
router.include_router(widget_router)
```

**7. Tests** — mirror the existing structure under `tests/`.
The `conftest.py` fixtures work for any new model.

New resources inherit tracing, metrics, error handling,
rate limiting, and AOP logging automatically.
"""
)


def _write_readme(output_dir: Path) -> None:
    dest = output_dir / TEMPLATE_DIR_NAME / "README.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_TEMPLATE_README, encoding="utf-8")


def _copy_project_files(output_dir: Path) -> int:
    template_dir = output_dir / TEMPLATE_DIR_NAME
    files = _collect_files()
    copied = 0

    for rel_path in files:
        src = PROJECT_ROOT / rel_path
        dest_rel = _compute_dest_path(rel_path)
        dest = template_dir / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)

        if _is_binary(src):
            shutil.copy2(src, dest)
        else:
            try:
                content = src.read_text(encoding="utf-8")
            except Exception:
                shutil.copy2(src, dest)
            else:
                content = _apply_replacements(content)
                dest.write_text(content, encoding="utf-8")

        copied += 1

    return copied


def main() -> int:
    args = _parse_args()
    output_dir: Path = args.output.resolve()

    if output_dir.exists():
        if not args.force:
            print(
                f"ERROR: Output directory already exists: {output_dir}\n"
                "Use --force to overwrite.",
                file=sys.stderr,
            )
            return 1
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)

    print(f"Building Cookiecutter template at: {output_dir}\n")

    _write_cookiecutter_json(output_dir)
    print("  Created: cookiecutter.json")

    _write_post_gen_hook(output_dir)
    print("  Created: hooks/post_gen_project.py")

    _write_readme(output_dir)
    print("  Created: README.md")

    count = _copy_project_files(output_dir)
    print(f"\n  Copied {count} files into {TEMPLATE_DIR_NAME}/")

    print(f"\nDone! Cookiecutter template is ready at: {output_dir}")
    print("\nUsage:")
    print(f"  cookiecutter {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
