from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from prometheus_fastapi_instrumentator import Instrumentator

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_prometheus(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus metrics enabled at /metrics")
