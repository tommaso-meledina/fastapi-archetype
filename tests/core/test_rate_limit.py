from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_get_dummies_includes_rate_limit_headers(client: TestClient) -> None:
    response = client.get("/v1/dummies")
    assert response.status_code == 200
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers


def test_post_dummies_includes_rate_limit_headers(client: TestClient) -> None:
    response = client.post("/v1/dummies", json={"name": "RateTest"})
    assert response.status_code == 201
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers


def test_exceeding_post_rate_limit_returns_429(client: TestClient) -> None:
    for _ in range(10):
        client.post("/v1/dummies", json={"name": "Flood"})
    response = client.post("/v1/dummies", json={"name": "OverLimit"})
    assert response.status_code == 429
    data = response.json()
    assert data["errorCode"] == "RATE_LIMITED"
    assert data["message"] == "Rate limit exceeded"
    assert "detail" in data


def test_rate_limited_response_body_structure(client: TestClient) -> None:
    for _ in range(10):
        client.post("/v1/dummies", json={"name": "Flood"})
    response = client.post("/v1/dummies", json={"name": "OverLimit"})
    assert response.status_code == 429
    data = response.json()
    assert set(data.keys()) == {"errorCode", "message", "detail"}


def test_v2_get_dummies_includes_rate_limit_headers(client: TestClient) -> None:
    response = client.get("/v2/dummies")
    assert response.status_code == 200
    assert "x-ratelimit-limit" in response.headers


def test_health_endpoint_not_rate_limited(client: TestClient) -> None:
    for _ in range(20):
        response = client.get("/health")
    assert response.status_code == 200
    assert "x-ratelimit-limit" not in response.headers


def test_remaining_decrements_on_successive_requests(
    client: TestClient,
) -> None:
    r1 = client.get("/v1/dummies")
    r2 = client.get("/v1/dummies")
    remaining1 = int(r1.headers["x-ratelimit-remaining"])
    remaining2 = int(r2.headers["x-ratelimit-remaining"])
    assert remaining2 == remaining1 - 1
