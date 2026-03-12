from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV2Contract
from fastapi_archetype.services.factory import build_dummy_service_v2


def get_dummy_service_v2() -> DummyServiceV2Contract:
    settings = AppSettings()
    return build_dummy_service_v2(settings)
