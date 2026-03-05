from __future__ import annotations

import logging
import os

import pytest
from fastapi import APIRouter, Depends, Request, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter

os.environ.setdefault("AUTH_TYPE", "none")

from fastapi_archetype.auth.dependencies import require_auth, require_role
from fastapi_archetype.auth.models import Role
from fastapi_archetype.main import app

_stub_logger = logging.getLogger("fastapi_archetype.test_stubs")


class _StubPayload(BaseModel):
    value: str


_test_router = APIRouter(prefix="/test", tags=["Test Stubs"])
_require_admin_role = require_role(Role.ADMIN)


@_test_router.get("/open")
@limiter.limit("100/minute")
def _stub_get_open(request: Request, response: Response) -> dict[str, str]:
    _stub_logger.debug("stub endpoint called")
    return {"status": "ok"}


@_test_router.post("/open", status_code=201)
@limiter.limit("10/minute")
def _stub_post_open(
    request: Request, payload: _StubPayload, response: Response
) -> dict[str, str]:
    return {"value": payload.value}


@_test_router.post("/auth-required", status_code=201)
@limiter.limit("10/minute")
def _stub_post_auth_required(
    request: Request,
    payload: _StubPayload,
    response: Response,
    principal=Depends(require_auth),
) -> dict[str, str]:
    _ = principal
    return {"value": payload.value}


@_test_router.post("/admin-required", status_code=201)
@limiter.limit("10/minute")
def _stub_post_admin_required(
    request: Request,
    payload: _StubPayload,
    response: Response,
    principal=Depends(_require_admin_role),
) -> dict[str, str]:
    _ = principal
    return {"value": payload.value}


app.include_router(_test_router)


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


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
