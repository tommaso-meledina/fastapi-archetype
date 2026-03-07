from __future__ import annotations

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session

from fastapi_archetype.core import database
from fastapi_archetype.core.config import AppSettings


def test_get_engine_without_settings_builds_default_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(database, "_engine", None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DEBUG", "false")

    try:
        engine = database.get_engine()

        assert str(engine.url) == "sqlite://"
        assert isinstance(engine.pool, StaticPool)
    finally:
        database.dispose_engine()


def test_get_session_yields_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(database, "_engine", None)
    try:
        database.get_engine(AppSettings())

        generator = database.get_session()
        session = next(generator)

        assert isinstance(session, Session)

        with pytest.raises(StopIteration):
            next(generator)
    finally:
        database.dispose_engine()


def test_dispose_engine_resets_global_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(database, "_engine", None)
    database.get_engine(AppSettings())

    database.dispose_engine()

    assert database._engine is None


def test_invalid_database_url_raises_at_engine_creation() -> None:
    database.dispose_engine()
    settings = AppSettings(database_url="not-a-valid-url://")
    with pytest.raises(ValueError, match="Invalid DATABASE_URL"):
        database.get_engine(settings)
