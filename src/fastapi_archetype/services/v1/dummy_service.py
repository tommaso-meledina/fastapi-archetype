from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.services.factory import build_dummy_service

if TYPE_CHECKING:
    from fastapi_archetype.services.contracts.dummy_service import (
        DummyServiceContract,
    )


def get_dummy_service() -> DummyServiceContract:
    settings = AppSettings()
    return build_dummy_service(settings)
