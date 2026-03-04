from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Counters:
    dummies_created_total: Counter


@dataclass(frozen=True)
class Metrics:
    counters: Counters


metrics = Metrics(
    counters=Counters(
        dummies_created_total=Counter(
            "dummies_created_total",
            "Total number of dummy resources created",
            labelnames=["api_version"],
        ),
    ),
)


def setup_prometheus(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus metrics enabled at /metrics")
