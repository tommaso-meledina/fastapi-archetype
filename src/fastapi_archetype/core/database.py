from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from fastapi_archetype.core.config import AppSettings

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy import Engine

_engine: Engine | None = None


def get_engine(settings: AppSettings | None = None) -> Engine:
    global _engine  # noqa: PLW0603
    if _engine is None:
        if settings is None:
            settings = AppSettings()
        kwargs: dict = {"echo": settings.debug}
        if settings.db_driver == "sqlite":
            kwargs["connect_args"] = {"check_same_thread": False}
            kwargs["poolclass"] = StaticPool
        _engine = create_engine(settings.database_url, **kwargs)
    return _engine


def get_session() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session


def dispose_engine() -> None:
    global _engine  # noqa: PLW0603
    if _engine is not None:
        _engine.dispose()
        _engine = None
