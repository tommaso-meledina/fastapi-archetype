from __future__ import annotations

from fastapi_archetype.models.dto.v1.dummy import (
    GetDummiesResponse,
    PostDummiesRequest,
    PostDummiesResponse,
)
from fastapi_archetype.models.entities.dummy import Dummy


def entity_to_get_response(entity: Dummy) -> GetDummiesResponse:
    return GetDummiesResponse.model_validate(
        entity.model_dump(include={"name", "description"})
    )


def entity_to_post_response(entity: Dummy) -> PostDummiesResponse:
    return PostDummiesResponse.model_validate(entity.model_dump())


def dto_to_entity(dto: PostDummiesRequest) -> Dummy:
    return Dummy.model_validate(dto.model_dump())
