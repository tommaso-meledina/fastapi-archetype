from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV1Contract
from fastapi_archetype.services.factory import build_dummy_service_v1


def get_dummy_service_v1() -> DummyServiceV1Contract:
    settings = AppSettings()
    return build_dummy_service_v1(settings)
