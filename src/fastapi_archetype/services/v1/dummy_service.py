from fastapi_archetype.core.config import settings
from fastapi_archetype.services.factory import DummyServiceV1, build_dummy_service_v1


def get_dummy_service_v1() -> DummyServiceV1:
    return build_dummy_service_v1(settings)
