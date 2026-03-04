from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

V2_SERVICE_LOGGER = "fastapi_archetype.services.v2.dummy_service"


def test_v2_list_dummies_empty(client: TestClient) -> None:
    response = client.get("/v2/dummies")
    assert response.status_code == 200
    assert response.json() == []


def test_v2_create_dummy_returns_201(client: TestClient) -> None:
    response = client.post(
        "/v2/dummies", json={"name": "V2Widget", "description": "A v2 test widget"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "V2Widget"
    assert data["description"] == "A v2 test widget"
    assert "id" in data


def test_v2_list_dummies_populated(client: TestClient) -> None:
    client.post("/v2/dummies", json={"name": "Alpha"})
    client.post("/v2/dummies", json={"name": "Bravo"})
    response = client.get("/v2/dummies")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_v1_and_v2_share_data(client: TestClient) -> None:
    client.post("/v1/dummies", json={"name": "SharedItem"})
    v2_response = client.get("/v2/dummies")
    names = [d["name"] for d in v2_response.json()]
    assert "SharedItem" in names


def test_v2_logs_on_list(client: TestClient, caplog: logging.LogRecord) -> None:
    with caplog.at_level(logging.INFO, logger=V2_SERVICE_LOGGER):
        client.get("/v2/dummies")
    assert any("v2 get_all_dummies returned" in r.message for r in caplog.records)


def test_v2_logs_on_create(client: TestClient, caplog: logging.LogRecord) -> None:
    with caplog.at_level(logging.INFO, logger=V2_SERVICE_LOGGER):
        client.post("/v2/dummies", json={"name": "Logged"})
    assert any("v2 create_dummy" in r.message for r in caplog.records)
