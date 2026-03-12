from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.services.contracts.dummy_service import (
    DummyServiceV1Contract,
    DummyServiceV2Contract,
)
from fastapi_archetype.services.v1.implementations.default_dummy_service import (
    DefaultDummyServiceV1,
)
from fastapi_archetype.services.v1.implementations.mock_dummy_service import (
    MockDummyServiceV1,
)
from fastapi_archetype.services.v2.implementations.default_dummy_service import (
    DefaultDummyServiceV2,
)
from fastapi_archetype.services.v2.implementations.mock_dummy_service import (
    MockDummyServiceV2,
)


def build_dummy_service_v1(settings: AppSettings) -> DummyServiceV1Contract:
    if settings.profile == "mock":
        return MockDummyServiceV1()
    return DefaultDummyServiceV1()


def build_dummy_service_v2(settings: AppSettings) -> DummyServiceV2Contract:
    if settings.profile == "mock":
        return MockDummyServiceV2()
    return DefaultDummyServiceV2()
