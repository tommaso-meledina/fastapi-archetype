from __future__ import annotations

from fastapi_archetype.models.dto.v1.dummy import (
    GetDummiesResponse,
    PostDummiesRequest,
    PostDummiesResponse,
    PutDummiesRequest,
)
from fastapi_archetype.models.entities.dummy import Dummy


def _name_initial(name: str) -> str:
    return name[0] if name else ""


def entity_to_get_response(entity: Dummy) -> GetDummiesResponse:
    return GetDummiesResponse(
        uuid=entity.uuid,
        name=entity.name,
        description=entity.description,
        name_initial=_name_initial(entity.name),
    )


def entity_to_post_response(entity: Dummy) -> PostDummiesResponse:
    return PostDummiesResponse(
        uuid=entity.uuid,
        name=entity.name,
        description=entity.description,
    )


def dto_to_entity(dto: PostDummiesRequest) -> Dummy:
    return Dummy.model_validate(dto.model_dump())


def put_dto_to_entity(
    existing: Dummy,
    dto: PutDummiesRequest,
) -> Dummy:
    return Dummy(
        id=existing.id,
        uuid=existing.uuid,
        name=dto.name,
        description=dto.description,
    )
