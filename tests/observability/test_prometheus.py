from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.models.dummy import Dummy
from fastapi_archetype.observability.prometheus import metrics
from fastapi_archetype.services.v1.dummy_service import create_dummy

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

_counter = metrics.counters.dummies_created_total


def _v1_value() -> float:
    return _counter.labels(api_version="v1")._value.get()


def _v2_value() -> float:
    return _counter.labels(api_version="v2")._value.get()


def test_v1_counter_increments_on_create(session: Session) -> None:
    before = _v1_value()
    create_dummy(session, Dummy(name="CountMe"))
    assert _v1_value() == before + 1


def test_v1_counter_increments_multiple(session: Session) -> None:
    before = _v1_value()
    create_dummy(session, Dummy(name="First"))
    create_dummy(session, Dummy(name="Second"))
    assert _v1_value() == before + 2


def test_v1_counter_unchanged_on_failed_creation(client: TestClient) -> None:
    before = _v1_value()
    client.post("/v1/dummies")
    assert _v1_value() == before


def test_v2_counter_increments_via_endpoint(client: TestClient) -> None:
    before = _v2_value()
    client.post("/v2/dummies", json={"name": "V2Item"})
    assert _v2_value() == before + 1


def test_v1_and_v2_counters_are_independent(client: TestClient) -> None:
    v1_before = _v1_value()
    v2_before = _v2_value()
    client.post("/v1/dummies", json={"name": "OnlyV1"})
    assert _v1_value() == v1_before + 1
    assert _v2_value() == v2_before


def test_metrics_endpoint_includes_labeled_metric(client: TestClient) -> None:
    client.post("/v1/dummies", json={"name": "MetricTest"})
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "dummies_created_total" in body
    assert 'api_version="v1"' in body
    assert "Total number of dummy resources created" in body


def test_metrics_counter_reflects_posts(client: TestClient) -> None:
    before = _v1_value()
    client.post("/v1/dummies", json={"name": "A"})
    client.post("/v1/dummies", json={"name": "B"})
    after = _v1_value()
    assert after == before + 2

    response = client.get("/metrics")
    body = response.text
    for line in body.splitlines():
        if line.startswith("dummies_created_total{") and 'api_version="v1"' in line:
            reported = float(line.split()[-1])
            assert reported == after
            break
    else:
        raise AssertionError(
            'dummies_created_total{api_version="v1"} not found in /metrics output'
        )
