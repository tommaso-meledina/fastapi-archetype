from fastapi_archetype.aop.logging_decorator import apply_logging
from fastapi_archetype.services.v1 import dummy as v1_dummy
from fastapi_archetype.services.v1 import mock_dummy as v1_mock_dummy
from fastapi_archetype.services.v2 import dummy as v2_dummy
from fastapi_archetype.services.v2 import mock_dummy as v2_mock_dummy

# This package's __init__ applies AOP logging decorators as a side effect;
# no symbols are re-exported at the package boundary.
__all__: list[str] = []

apply_logging(v1_dummy)
apply_logging(v1_mock_dummy)
apply_logging(v2_dummy)
apply_logging(v2_mock_dummy)
