from fastapi_archetype.aop.logging_decorator import apply_logging
from fastapi_archetype.services.v1 import dummy_service as v1_dummy_service
from fastapi_archetype.services.v2 import dummy_service as v2_dummy_service

apply_logging(v1_dummy_service)
apply_logging(v2_dummy_service)
