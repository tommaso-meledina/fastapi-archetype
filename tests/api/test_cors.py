from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

import fastapi_archetype.main as main_module

if TYPE_CHECKING:
    from fastapi import FastAPI


def _reload_main_app() -> FastAPI:
    module = importlib.reload(main_module)
    return module.app


@pytest.fixture(autouse=True)
def _restore_main_module() -> None:
    yield
    os.environ["ENV_FILE"] = ""
    os.environ.pop("CORS_ENABLED", None)
    os.environ.pop("CORS_ALLOW_ORIGINS", None)
    os.environ.pop("CORS_ALLOW_METHODS", None)
    os.environ.pop("CORS_ALLOW_HEADERS", None)
    os.environ.pop("CORS_ALLOW_CREDENTIALS", None)
    os.environ.pop("CORS_EXPOSE_HEADERS", None)
    _reload_main_app()


def test_cors_disabled_by_default_omits_cors_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENV_FILE", "")
    monkeypatch.delenv("CORS_ENABLED", raising=False)
    app = _reload_main_app()

    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "http://frontend.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_enabled_returns_preflight_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENV_FILE", "")
    monkeypatch.setenv("CORS_ENABLED", "true")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://frontend.example")
    monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST,OPTIONS")
    monkeypatch.setenv("CORS_ALLOW_HEADERS", "Authorization,Content-Type")
    app = _reload_main_app()

    with TestClient(app) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://frontend.example",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == (
        "http://frontend.example"
    )
