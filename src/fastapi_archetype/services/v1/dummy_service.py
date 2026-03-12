from functools import lru_cache

from fastapi_archetype.core.config import settings
from fastapi_archetype.services.factory import DummyServiceV1, build_dummy_service_v1


@lru_cache
def get_dummy_service_v1() -> DummyServiceV1:
    return build_dummy_service_v1(settings)
