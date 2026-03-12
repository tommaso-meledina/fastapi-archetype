from collections.abc import Callable
from dataclasses import dataclass

from sqlmodel import Session

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.models.entities.dummy import Dummy


@dataclass(frozen=True, kw_only=True)
class DummyServiceV1:
    """Callable fields dispatched to the configured profile's implementation."""

    get_all_dummies: Callable[[Session], list[Dummy]]
    get_dummy_by_uuid: Callable[[Session, str], Dummy | None]
    create_dummy: Callable[[Session, Dummy], Dummy]
    update_dummy: Callable[[Session, Dummy], Dummy]


@dataclass(frozen=True, kw_only=True)
class DummyServiceV2:
    """Callable fields dispatched to the configured profile's implementation."""

    get_all_dummies: Callable[[Session], list[Dummy]]
    create_dummy: Callable[[Session, Dummy], Dummy]


def build_dummy_service_v1(settings: AppSettings) -> DummyServiceV1:
    from fastapi_archetype.services.v1 import dummy as v1_dummy
    from fastapi_archetype.services.v1 import mock_dummy as v1_mock_dummy

    modules = {"default": v1_dummy, "mock": v1_mock_dummy}
    m = modules[settings.profile]
    return DummyServiceV1(
        get_all_dummies=m.get_all_dummies,
        get_dummy_by_uuid=m.get_dummy_by_uuid,
        create_dummy=m.create_dummy,
        update_dummy=m.update_dummy,
    )


def build_dummy_service_v2(settings: AppSettings) -> DummyServiceV2:
    from fastapi_archetype.services.v2 import dummy as v2_dummy
    from fastapi_archetype.services.v2 import mock_dummy as v2_mock_dummy

    modules = {"default": v2_dummy, "mock": v2_mock_dummy}
    m = modules[settings.profile]
    return DummyServiceV2(
        get_all_dummies=m.get_all_dummies,
        create_dummy=m.create_dummy,
    )
