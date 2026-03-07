from __future__ import annotations

from fastapi_archetype.models.dto.v1.dummy import (
    GetDummiesResponse,
    PostDummiesRequest,
    PostDummiesResponse,
)
from fastapi_archetype.models.entities.dummy import Dummy


def _name_initial(name: str) -> str:
    return name[0] if name else ""


def entity_to_get_response(entity: Dummy) -> GetDummiesResponse:
    return GetDummiesResponse(
        name=entity.name,
        description=entity.description,
        name_initial=_name_initial(entity.name),
    )


def entity_to_post_response(entity: Dummy) -> PostDummiesResponse:
    return PostDummiesResponse.model_validate(entity.model_dump())


def dto_to_entity(dto: PostDummiesRequest) -> Dummy:
    return Dummy.model_validate(dto.model_dump())
