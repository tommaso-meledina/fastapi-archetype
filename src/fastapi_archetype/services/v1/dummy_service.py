from fastapi_archetype.core.config import settings
from fastapi_archetype.services.contracts.dummy_service import DummyServiceV1Contract
from fastapi_archetype.services.factory import build_dummy_service_v1


def get_dummy_service_v1() -> DummyServiceV1Contract:
    return build_dummy_service_v1(settings)
