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
    assert "uuid" in data
    assert isinstance(data["uuid"], str)
    assert "id" not in data


def test_create_dummy_minimal(client: TestClient) -> None:
    response = client.post("/v1/dummies", json={"name": "Minimal"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal"
    assert data["description"] is None
    assert "uuid" in data
    assert "id" not in data


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
    # GET list: uuid, name, nameInitial (computed), description; never id
    expected_keys = {"uuid", "name", "nameInitial", "description"}
    assert set(items[0].keys()) == expected_keys
    assert "id" not in items[0]


def test_get_response_includes_computed_name_initial(client: TestClient) -> None:
    client.post("/v1/dummies", json={"name": "Alice", "description": "Test"})
    response = client.get("/v1/dummies")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    alice = next(i for i in items if i["name"] == "Alice")
    assert alice["nameInitial"] == "A"


def test_create_response_uses_camel_case_keys(client: TestClient) -> None:
    response = client.post(
        "/v1/dummies",
        json={"name": "CamelPost", "description": "keys check"},
    )
    assert response.status_code == 201
    expected_keys = {"uuid", "name", "description"}
    assert set(response.json().keys()) == expected_keys
    assert "id" not in response.json()


def test_unversioned_dummies_get_returns_404(client: TestClient) -> None:
    response = client.get("/dummies")
    assert response.status_code == 404


def test_unversioned_dummies_post_returns_404(client: TestClient) -> None:
    response = client.post("/dummies", json={"name": "ShouldFail"})
    assert response.status_code == 404


def test_put_dummy_success(client: TestClient) -> None:
    create_resp = client.post(
        "/v1/dummies",
        json={"name": "Original", "description": "Before"},
    )
    assert create_resp.status_code == 201
    uuid = create_resp.json()["uuid"]
    put_resp = client.put(
        f"/v1/dummies/{uuid}",
        json={"uuid": uuid, "name": "Updated", "description": "After"},
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["uuid"] == uuid
    assert data["name"] == "Updated"
    assert data["description"] == "After"
    assert data["nameInitial"] == "U"
    get_resp = client.get("/v1/dummies")
    items = [i for i in get_resp.json() if i["uuid"] == uuid]
    assert len(items) == 1
    assert items[0]["name"] == "Updated"


def test_put_dummy_path_body_uuid_mismatch_returns_400(client: TestClient) -> None:
    create_resp = client.post(
        "/v1/dummies",
        json={"name": "One", "description": "Desc"},
    )
    assert create_resp.status_code == 201
    uuid = create_resp.json()["uuid"]
    other_uuid = "00000000-0000-0000-0000-000000000000"
    put_resp = client.put(
        f"/v1/dummies/{uuid}",
        json={"uuid": other_uuid, "name": "Other", "description": None},
    )
    assert put_resp.status_code == 400
    data = put_resp.json()
    assert data["errorCode"] == "BAD_REQUEST"


def test_put_dummy_unknown_uuid_returns_404(client: TestClient) -> None:
    put_resp = client.put(
        "/v1/dummies/00000000-0000-0000-0000-000000000000",
        json={
            "uuid": "00000000-0000-0000-0000-000000000000",
            "name": "No",
            "description": None,
        },
    )
    assert put_resp.status_code == 404
    assert put_resp.json()["errorCode"] == "DUMMY_NOT_FOUND"
