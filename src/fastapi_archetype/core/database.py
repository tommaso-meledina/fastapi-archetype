from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import make_url
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from fastapi_archetype.core.config import AppSettings

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.engine import Engine

_engine: Engine | None = None

SQLITE_PREFIX = "sqlite://"


def create_sqlite_engine(
    url: str = SQLITE_PREFIX,
    *,
    echo: bool = False,
) -> Engine:
    """Create an engine for SQLite (StaticPool, check_same_thread=False)."""
    return create_engine(
        url,
        echo=echo,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_url_engine(url: str, *, echo: bool = False) -> Engine:
    """Create an engine from a given URL for non-SQLite backends."""
    return create_engine(url, echo=echo)


def get_engine(settings: AppSettings | None = None) -> Engine:
    global _engine  # noqa: PLW0603
    if _engine is None:
        if settings is None:
            settings = AppSettings()
        effective = settings.effective_database_url
        if effective.startswith(SQLITE_PREFIX):
            _engine = create_sqlite_engine(effective, echo=settings.debug)
        else:
            try:
                make_url(effective)
            except Exception as e:
                raise ValueError(f"Invalid DATABASE_URL: {effective!r}. {e!s}") from e
            _engine = create_url_engine(effective, echo=settings.debug)
    return _engine


def get_session() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session


def dispose_engine() -> None:
    global _engine  # noqa: PLW0603
    if _engine is not None:
        _engine.dispose()
        _engine = None
