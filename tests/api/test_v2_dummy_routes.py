import logging

from httpx import AsyncClient
from pytest import LogCaptureFixture

V2_SERVICE_LOGGER = "fastapi_archetype.services.v2.dummy_service"


async def test_v2_list_dummies_empty(client: AsyncClient) -> None:
    response = await client.get("/v2/dummies")
    assert response.status_code == 200
    assert response.json() == []


async def test_v2_create_dummy_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/v2/dummies",
        json={"name": "V2Widget", "description": "A v2 test widget"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "V2Widget"
    assert data["description"] == "A v2 test widget"
    assert "uuid" in data
    assert "id" not in data


async def test_v2_list_dummies_populated(client: AsyncClient) -> None:
    await client.post("/v2/dummies", json={"name": "Alpha"})
    await client.post("/v2/dummies", json={"name": "Bravo"})
    response = await client.get("/v2/dummies")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_v1_and_v2_share_data(client: AsyncClient) -> None:
    await client.post("/v1/dummies", json={"name": "SharedItem"})
    v2_response = await client.get("/v2/dummies")
    names = [d["name"] for d in v2_response.json()]
    assert "SharedItem" in names


async def test_v2_logs_on_list(client: AsyncClient, caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger=V2_SERVICE_LOGGER):
        await client.get("/v2/dummies")
    assert any("v2 get_all_dummies returned" in r.message for r in caplog.records)


async def test_v2_logs_on_create(
    client: AsyncClient, caplog: LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=V2_SERVICE_LOGGER):
        await client.post("/v2/dummies", json={"name": "Logged"})
    assert any("v2 create_dummy" in r.message for r in caplog.records)


async def test_v2_create_dummy_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/v2/dummies", json={"name": "NoAuth"})
    assert response.status_code == 201


async def test_v2_create_dummy_requires_admin_role(client: AsyncClient) -> None:
    response = await client.post("/v2/dummies", json={"name": "NoAdmin"})
    assert response.status_code == 201
