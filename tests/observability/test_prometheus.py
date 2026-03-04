from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.observability.prometheus import DUMMIES_CREATED_TOTAL
from fastapi_archetype.services.dummy_service import create_dummy

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def test_custom_counter_increments_on_create(session: Session) -> None:
    before = DUMMIES_CREATED_TOTAL._value.get()
    create_dummy(session, Dummy(name="CountMe"))
    assert DUMMIES_CREATED_TOTAL._value.get() == before + 1


def test_custom_counter_increments_multiple(session: Session) -> None:
    before = DUMMIES_CREATED_TOTAL._value.get()
    create_dummy(session, Dummy(name="First"))
    create_dummy(session, Dummy(name="Second"))
    assert DUMMIES_CREATED_TOTAL._value.get() == before + 2


def test_counter_unchanged_on_failed_creation(client: TestClient) -> None:
    before = DUMMIES_CREATED_TOTAL._value.get()
    client.post("/dummies")
    assert DUMMIES_CREATED_TOTAL._value.get() == before


def test_metrics_endpoint_includes_custom_metric(client: TestClient) -> None:
    client.post("/dummies", json={"name": "MetricTest"})
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "dummies_created_total" in body
    assert "Total number of dummy resources created" in body


def test_metrics_counter_reflects_posts(client: TestClient) -> None:
    before = DUMMIES_CREATED_TOTAL._value.get()
    client.post("/dummies", json={"name": "A"})
    client.post("/dummies", json={"name": "B"})
    after = DUMMIES_CREATED_TOTAL._value.get()
    assert after == before + 2

    response = client.get("/metrics")
    body = response.text
    for line in body.splitlines():
        if line.startswith("dummies_created_total "):
            reported = float(line.split()[1])
            assert reported == after
            break
    else:
        raise AssertionError("dummies_created_total not found in /metrics output")
