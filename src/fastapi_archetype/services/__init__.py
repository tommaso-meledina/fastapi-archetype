from fastapi_archetype.aop.logging_decorator import apply_logging
from fastapi_archetype.services.v1.implementations import (
    default_dummy_service as v1_default_dummy_service,
)
from fastapi_archetype.services.v1.implementations import (
    mock_dummy_service as v1_mock_dummy_service,
)
from fastapi_archetype.services.v2.implementations import (
    default_dummy_service as v2_default_dummy_service,
)
from fastapi_archetype.services.v2.implementations import (
    mock_dummy_service as v2_mock_dummy_service,
)

apply_logging(v1_default_dummy_service)
apply_logging(v1_mock_dummy_service)
apply_logging(v2_default_dummy_service)
apply_logging(v2_mock_dummy_service)
