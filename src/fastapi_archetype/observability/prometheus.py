from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)

DUMMIES_CREATED_TOTAL = Counter(
    "dummies_created_total",
    "Total number of dummy resources created",
)


def setup_prometheus(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus metrics enabled at /metrics")
