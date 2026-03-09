from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.services.factory import build_dummy_service_v2

if TYPE_CHECKING:
    from fastapi_archetype.services.contracts.dummy_service import (
        DummyServiceV2Contract,
    )


def get_dummy_service_v2() -> DummyServiceV2Contract:
    settings = AppSettings()
    return build_dummy_service_v2(settings)
