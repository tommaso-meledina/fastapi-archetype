from functools import lru_cache

from fastapi_archetype.core.config import settings
from fastapi_archetype.services.factory import DummyServiceV2, build_dummy_service_v2


@lru_cache
def get_dummy_service_v2() -> DummyServiceV2:
    return build_dummy_service_v2(settings)
