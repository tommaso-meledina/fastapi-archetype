"""Tests for profile-driven service selection (PROFILE=default vs PROFILE=mock)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import fastapi_archetype.core.config as core_config_module
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app
from fastapi_archetype.services.factory import DummyServiceV1, DummyServiceV2
from fastapi_archetype.services.v1 import mock_dummy as v1_mock_dummy
from fastapi_archetype.services.v1.dummy_service import get_dummy_service_v1
from fastapi_archetype.services.v1.mock_dummy import MOCK_UUID_1
from fastapi_archetype.services.v2 import mock_dummy as v2_mock_dummy
from fastapi_archetype.services.v2.dummy_service import get_dummy_service_v2


@pytest.fixture(name="client_with_mock_v1_simple")
async def client_with_mock_v1_simple_fixture(session: AsyncSession):
    mock_svc = DummyServiceV1(
        get_all_dummies=v1_mock_dummy.get_all_dummies,
        get_dummy_by_uuid=v1_mock_dummy.get_dummy_by_uuid,
        create_dummy=v1_mock_dummy.create_dummy,
        update_dummy=v1_mock_dummy.update_dummy,
    )

    async def _override_session():
        yield session

    def _override_svc():
        return mock_svc

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_dummy_service_v1] = _override_svc
    limiter.reset()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def test_v1_mock_list_create_put_without_db(
    client_with_mock_v1_simple: AsyncClient,
) -> None:
    """Mock returns static list; create/put return static responses (no DB)."""
    r = await client_with_mock_v1_simple.get("/v1/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock One"
    assert items[0]["uuid"] == MOCK_UUID_1

    r = await client_with_mock_v1_simple.post(
        "/v1/dummies",
        json={"name": "Ignored", "description": "ignored"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Mock Created"
    assert data["uuid"] == "00000000-0000-0000-0000-000000000002"

    r = await client_with_mock_v1_simple.put(
        f"/v1/dummies/{MOCK_UUID_1}",
        json={
            "uuid": MOCK_UUID_1,
            "name": "Ignored",
            "description": "ignored",
        },
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Mock Updated"


@pytest.fixture(name="client_with_mock_v2")
async def client_with_mock_v2_fixture(session: AsyncSession):
    mock_svc = DummyServiceV2(
        get_all_dummies=v2_mock_dummy.get_all_dummies,
        create_dummy=v2_mock_dummy.create_dummy,
    )

    async def _override_session():
        yield session

    def _override_svc():
        return mock_svc

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_dummy_service_v2] = _override_svc
    limiter.reset()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def test_v2_mock_list_create_without_db(
    client_with_mock_v2: AsyncClient,
) -> None:
    """Mock returns static list; create returns static response (no DB)."""
    r = await client_with_mock_v2.get("/v2/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock V2"

    r = await client_with_mock_v2.post(
        "/v2/dummies",
        json={"name": "Ignored", "description": "ignored"},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Mock Created V2"


async def test_profile_mock_v1_returns_static_list(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PROFILE=mock: GET /v1/dummies returns 200 and static mock list (no DB)."""
    monkeypatch.setattr(core_config_module.settings, "profile", "mock")
    r = await client.get("/v1/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock One"


async def test_profile_mock_v2_returns_static_list(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PROFILE=mock: GET /v2/dummies returns 200 and static mock list (no DB)."""
    monkeypatch.setattr(core_config_module.settings, "profile", "mock")
    r = await client.get("/v2/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock V2"
