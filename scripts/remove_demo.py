#!/usr/bin/env python3
"""Remove Dummy CRUD demo boilerplate from the fastapi-archetype project.

Run from the project root:  python3 scripts/remove_demo.py

Requires a clean git working tree (no uncommitted changes).
Uses only the Python standard library.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILES_TO_DELETE = [
    "src/fastapi_archetype/models/dummy.py",
    "src/fastapi_archetype/api/v1/dummy_routes.py",
    "src/fastapi_archetype/api/v2/dummy_routes.py",
    "src/fastapi_archetype/services/v1/dummy_service.py",
    "src/fastapi_archetype/services/v2/dummy_service.py",
    "tests/api/test_dummy_routes.py",
    "tests/api/test_v2_dummy_routes.py",
    "tests/services/v1/test_dummy_service.py",
    "tests/services/v2/test_dummy_service.py",
]


def _git_tree_is_clean() -> bool:
    try:
        subprocess.run(
            ["git", "diff", "--quiet", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "diff", "--cached", "--quiet", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return False
    return True


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
        "router = APIRouter(prefix=\"/v1\")\n"
    )
    _write(path, content)


def _edit_api_v2_init(path: Path) -> None:
    content = (
        "from __future__ import annotations\n"
        "\n"
        "from fastapi import APIRouter\n"
        "\n"
        "router = APIRouter(prefix=\"/v2\")\n"
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


_EDIT_DISPATCH: list[tuple[str, callable]] = [
    ("src/fastapi_archetype/core/constants.py", _edit_constants),
    ("src/fastapi_archetype/core/errors.py", _edit_errors),
    ("src/fastapi_archetype/core/config.py", _edit_config),
    ("src/fastapi_archetype/services/__init__.py", _edit_services_init),
    ("src/fastapi_archetype/api/v1/__init__.py", _edit_api_v1_init),
    ("src/fastapi_archetype/api/v2/__init__.py", _edit_api_v2_init),
    ("src/fastapi_archetype/observability/prometheus.py", _edit_prometheus),
    (".env.example", _edit_env_example),
]


def main() -> int:
    if not _git_tree_is_clean():
        print(
            "ERROR: Git working tree has uncommitted changes.\n"
            "Please commit or stash your changes before running this script.",
            file=sys.stderr,
        )
        return 1

    print("Removing Dummy CRUD demo boilerplate...")

    for rel_path in FILES_TO_DELETE:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            full_path.unlink()
            print(f"  Deleted: {rel_path}")
        else:
            print(f"  Skipped (not found): {rel_path}")

    for rel_path, edit_fn in _EDIT_DISPATCH:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            edit_fn(full_path)
            print(f"  Edited:  {rel_path}")
        else:
            print(f"  Skipped (not found): {rel_path}")

    print("\nDone! The Dummy demo has been removed.")
    print("Next steps:")
    print("  1. Review the changes: git diff")
    print("  2. Run the test suite: pytest")
    print("  3. Commit: git add -A && git commit -m 'chore: remove demo boilerplate'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
