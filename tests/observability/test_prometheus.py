from httpx import AsyncClient
from prometheus_client import Counter

_test_counter = Counter(
    "test_operations_total",
    "Test counter for prometheus infrastructure validation",
    labelnames=["operation"],
)


def _op_value(operation: str) -> float:
    # noinspection PyProtectedMember
    return _test_counter.labels(operation=operation)._value.get()


def test_counter_increments_on_call() -> None:
    before = _op_value("create")
    _test_counter.labels(operation="create").inc()
    assert _op_value("create") == before + 1


def test_counter_increments_multiple() -> None:
    before = _op_value("create")
    _test_counter.labels(operation="create").inc()
    _test_counter.labels(operation="create").inc()
    assert _op_value("create") == before + 2


def test_labels_are_independent() -> None:
    create_before = _op_value("create")
    read_before = _op_value("read")
    _test_counter.labels(operation="create").inc()
    assert _op_value("create") == create_before + 1
    assert _op_value("read") == read_before


async def test_metrics_endpoint_returns_prometheus_format(
    client: AsyncClient,
) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "http" in body.lower()


async def test_metrics_endpoint_exposes_custom_counter(
    client: AsyncClient,
) -> None:
    _test_counter.labels(operation="create").inc()
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "test_operations_total" in body
    assert 'operation="create"' in body
    assert "Test counter for prometheus infrastructure validation" in body


async def test_counter_value_reflected_at_metrics_endpoint(
    client: AsyncClient,
) -> None:
    before = _op_value("create")
    _test_counter.labels(operation="create").inc()
    _test_counter.labels(operation="create").inc()
    after = _op_value("create")
    assert after == before + 2

    response = await client.get("/metrics")
    body = response.text
    for line in body.splitlines():
        if line.startswith("test_operations_total{") and 'operation="create"' in line:
            reported = float(line.split()[-1])
            assert reported == after
            break
    else:
        raise AssertionError(
            'test_operations_total{operation="create"} not found in /metrics output'
        )


async def test_http_auto_instrumentation_present(client: AsyncClient) -> None:
    await client.get("/health")
    response = await client.get("/metrics")
    body = response.text
    assert "http_request" in body or "http_requests" in body
