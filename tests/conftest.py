from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter

os.environ.setdefault("AUTH_TYPE", "none")

from fastapi_archetype.main import app


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    limiter.reset()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
