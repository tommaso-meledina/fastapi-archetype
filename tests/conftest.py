import logging
import os

import pytest
from fastapi import APIRouter, Depends, Request, Response
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

os.environ["ENV_FILE"] = ""
os.environ.setdefault("AUTH_TYPE", "none")

from fastapi_archetype.auth.dependencies import require_auth, require_role
from fastapi_archetype.auth.models import Role
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app
from fastapi_archetype.services.v1.dummy_service import get_dummy_service_v1
from fastapi_archetype.services.v2.dummy_service import get_dummy_service_v2

_stub_logger = logging.getLogger("fastapi_archetype.test_stubs")


class _StubPayload(BaseModel):
    value: str


_test_router = APIRouter(prefix="/test", tags=["Test Stubs"])
_require_admin_role = require_role(Role.ADMIN)


@_test_router.get("/open")
@limiter.limit("100/minute")
async def _stub_get_open(request: Request, response: Response) -> dict[str, str]:
    _stub_logger.debug("stub endpoint called")
    return {"status": "ok"}


@_test_router.post("/open", status_code=201)
@limiter.limit("10/minute")
async def _stub_post_open(
    request: Request, payload: _StubPayload, response: Response
) -> dict[str, str]:
    return {"value": payload.value}


@_test_router.post("/auth-required", status_code=201)
@limiter.limit("10/minute")
async def _stub_post_auth_required(
    request: Request,
    payload: _StubPayload,
    response: Response,
    principal=Depends(require_auth),
) -> dict[str, str]:
    _ = principal
    return {"value": payload.value}


@_test_router.post("/admin-required", status_code=201)
@limiter.limit("10/minute")
async def _stub_post_admin_required(
    request: Request,
    payload: _StubPayload,
    response: Response,
    principal=Depends(_require_admin_role),
) -> dict[str, str]:
    _ = principal
    return {"value": payload.value}


app.include_router(_test_router)


@pytest.fixture(autouse=True)
def _clear_service_caches() -> None:
    """Clear lru_cache on service DI shims before each test to ensure isolation.

    The shims are cached for production efficiency, but tests may monkeypatch
    settings.profile or override dependencies — the cache must not carry over.
    """
    get_dummy_service_v1.cache_clear()
    get_dummy_service_v2.cache_clear()


@pytest.fixture(name="engine", scope="session")
async def engine_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(name="session")
async def session_fixture(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest.fixture(name="client")
async def client_fixture(session):
    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    limiter.reset()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
