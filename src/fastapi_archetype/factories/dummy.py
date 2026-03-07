from __future__ import annotations

from fastapi_archetype.models.dto.v1.dummy import GetDummiesResponse, PostDummiesRequest
from fastapi_archetype.models.entities.dummy import Dummy


def entity_to_dto(entity: Dummy) -> GetDummiesResponse:
    return GetDummiesResponse.model_validate(entity.model_dump())


def dto_to_entity(dto: PostDummiesRequest) -> Dummy:
    return Dummy.model_validate(dto.model_dump())
