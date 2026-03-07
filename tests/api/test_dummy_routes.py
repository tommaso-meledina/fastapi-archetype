from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_list_dummies_empty(client: TestClient) -> None:
    response = client.get("/v1/dummies")
    assert response.status_code == 200
    assert response.json() == []


def test_create_dummy_returns_201(client: TestClient) -> None:
    response = client.post(
        "/v1/dummies",
        json={"name": "Widget", "description": "A test widget"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["description"] == "A test widget"
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_dummy_minimal(client: TestClient) -> None:
    response = client.post("/v1/dummies", json={"name": "Minimal"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal"
    assert data["description"] is None


def test_list_dummies_populated(client: TestClient) -> None:
    client.post("/v1/dummies", json={"name": "First"})
    client.post("/v1/dummies", json={"name": "Second"})
    response = client.get("/v1/dummies")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    names = {item["name"] for item in items}
    assert names == {"First", "Second"}


def test_create_dummy_invalid_no_body(client: TestClient) -> None:
    response = client.post("/v1/dummies")
    assert response.status_code == 422
    data = response.json()
    assert data["errorCode"] == "VALIDATION_ERROR"
    assert data["message"] == "Request validation failed"
    assert data["detail"] is not None


def test_create_dummy_invalid_wrong_type(client: TestClient) -> None:
    response = client.post("/v1/dummies", json=[1, 2, 3])
    assert response.status_code == 422
    data = response.json()
    assert data["errorCode"] == "VALIDATION_ERROR"


def test_response_uses_camel_case_keys(client: TestClient) -> None:
    client.post("/v1/dummies", json={"name": "CamelTest", "description": "check keys"})
    response = client.get("/v1/dummies")
    items = response.json()
    assert len(items) >= 1
    # GET list does not expose id; only name and description (camelCase)
    expected_keys = {"name", "description"}
    assert set(items[0].keys()) == expected_keys


def test_create_response_uses_camel_case_keys(client: TestClient) -> None:
    response = client.post(
        "/v1/dummies",
        json={"name": "CamelPost", "description": "keys check"},
    )
    assert response.status_code == 201
    expected_keys = {"id", "name", "description"}
    assert set(response.json().keys()) == expected_keys


def test_unversioned_dummies_get_returns_404(client: TestClient) -> None:
    response = client.get("/dummies")
    assert response.status_code == 404


def test_unversioned_dummies_post_returns_404(client: TestClient) -> None:
    response = client.post("/dummies", json={"name": "ShouldFail"})
    assert response.status_code == 404
