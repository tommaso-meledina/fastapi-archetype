from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_archetype.services.v1.implementations.default_dummy_service import (
    DefaultDummyService,
)
from fastapi_archetype.services.v1.implementations.mock_dummy_service import (
    MockDummyService,
)
from fastapi_archetype.services.v2.implementations.default_dummy_service import (
    DefaultDummyServiceV2,
)
from fastapi_archetype.services.v2.implementations.mock_dummy_service import (
    MockDummyServiceV2,
)

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings
    from fastapi_archetype.services.contracts.dummy_service import (
        DummyServiceContract,
        DummyServiceV2Contract,
    )


def build_dummy_service(settings: AppSettings) -> DummyServiceContract:
    if settings.profile == "mock":
        return MockDummyService()
    return DefaultDummyService()


def build_dummy_service_v2(settings: AppSettings) -> DummyServiceV2Contract:
    if settings.profile == "mock":
        return MockDummyServiceV2()
    return DefaultDummyServiceV2()
