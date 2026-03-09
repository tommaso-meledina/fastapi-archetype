"""Tests for profile-driven service selection (PROFILE=default vs PROFILE=mock)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app
from fastapi_archetype.services.v1.dummy_service import get_dummy_service_v1
from fastapi_archetype.services.v1.implementations.mock_dummy_service import (
    MOCK_UUID_1,
    MockDummyServiceV1,
)
from fastapi_archetype.services.v2.dummy_service import get_dummy_service_v2
from fastapi_archetype.services.v2.implementations.mock_dummy_service import (
    MockDummyServiceV2,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


@pytest.fixture(name="client_with_mock_v1_simple")
def client_with_mock_v1_simple_fixture(session: Session):
    from fastapi.testclient import TestClient

    from fastapi_archetype.core.database import get_session

    mock_svc = MockDummyServiceV1()

    def _override_session():
        yield session

    def _override_svc():
        return mock_svc

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_dummy_service_v1] = _override_svc
    limiter.reset()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_v1_mock_list_create_put_without_db(
    client_with_mock_v1_simple: TestClient,
) -> None:
    """Mock returns static list; create/put return static responses (no DB)."""
    r = client_with_mock_v1_simple.get("/v1/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock One"
    assert items[0]["uuid"] == MOCK_UUID_1

    r = client_with_mock_v1_simple.post(
        "/v1/dummies",
        json={"name": "Ignored", "description": "ignored"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Mock Created"
    assert data["uuid"] == "00000000-0000-0000-0000-000000000002"

    r = client_with_mock_v1_simple.put(
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
def client_with_mock_v2_fixture(session: Session):
    from fastapi.testclient import TestClient

    from fastapi_archetype.core.database import get_session

    mock_svc = MockDummyServiceV2()

    def _override_session():
        yield session

    def _override_svc():
        return mock_svc

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_dummy_service_v2] = _override_svc
    limiter.reset()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_v2_mock_list_create_without_db(client_with_mock_v2: TestClient) -> None:
    """Mock returns static list; create returns static response (no DB)."""
    r = client_with_mock_v2.get("/v2/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock V2"

    r = client_with_mock_v2.post(
        "/v2/dummies",
        json={"name": "Ignored", "description": "ignored"},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Mock Created V2"


def test_profile_mock_v1_returns_static_list(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PROFILE=mock: GET /v1/dummies returns 200 and static mock list (no DB)."""
    monkeypatch.setenv("PROFILE", "mock")
    r = client.get("/v1/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock One"


def test_profile_mock_v2_returns_static_list(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PROFILE=mock: GET /v2/dummies returns 200 and static mock list (no DB)."""
    monkeypatch.setenv("PROFILE", "mock")
    r = client.get("/v2/dummies")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Static Mock V2"
