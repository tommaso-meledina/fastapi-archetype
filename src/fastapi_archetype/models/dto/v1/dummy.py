from __future__ import annotations

from pydantic import BaseModel, ConfigDict


def _to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class PostDummiesRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    name: str
    description: str | None = None


class GetDummiesResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    id: int | None = None
    name: str
    description: str | None = None


PostDummiesResponse = GetDummiesResponse
