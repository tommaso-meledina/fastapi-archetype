from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_list_dummies_empty(client: TestClient) -> None:
    response = client.get("/dummies")
    assert response.status_code == 200
    assert response.json() == []
