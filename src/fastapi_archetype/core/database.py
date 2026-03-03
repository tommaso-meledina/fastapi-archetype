from __future__ import annotations

from typing import TYPE_CHECKING

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
        _engine = create_engine(settings.database_url, echo=settings.debug)
    return _engine


def get_session() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session
