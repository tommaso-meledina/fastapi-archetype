from httpx import AsyncClient


async def test_get_includes_rate_limit_headers(client: AsyncClient) -> None:
    response = await client.get("/test/open")
    assert response.status_code == 200
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers


async def test_post_includes_rate_limit_headers(client: AsyncClient) -> None:
    response = await client.post("/test/open", json={"value": "RateTest"})
    assert response.status_code == 201
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers


async def test_exceeding_post_rate_limit_returns_429(client: AsyncClient) -> None:
    for _ in range(10):
        await client.post("/test/open", json={"value": "Flood"})
    response = await client.post("/test/open", json={"value": "OverLimit"})
    assert response.status_code == 429
    data = response.json()
    assert data["errorCode"] == "RATE_LIMITED"
    assert data["message"] == "Rate limit exceeded"
    assert "detail" in data


async def test_rate_limited_response_body_structure(client: AsyncClient) -> None:
    for _ in range(10):
        await client.post("/test/open", json={"value": "Flood"})
    response = await client.post("/test/open", json={"value": "OverLimit"})
    assert response.status_code == 429
    data = response.json()
    assert set(data.keys()) == {"errorCode", "message", "detail"}


async def test_health_endpoint_not_rate_limited(client: AsyncClient) -> None:
    response = await client.get("/health")
    for _ in range(19):
        response = await client.get("/health")
    assert response.status_code == 200
    assert "x-ratelimit-limit" not in response.headers


async def test_remaining_decrements_on_successive_requests(
    client: AsyncClient,
) -> None:
    r1 = await client.get("/test/open")
    r2 = await client.get("/test/open")
    remaining1 = int(r1.headers["x-ratelimit-remaining"])
    remaining2 = int(r2.headers["x-ratelimit-remaining"])
    assert remaining2 == remaining1 - 1
