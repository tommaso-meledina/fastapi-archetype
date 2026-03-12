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

    uuid: str
    name: str
    name_initial: str
    description: str | None = None


class PostDummiesResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    uuid: str
    name: str
    description: str | None = None


class PutDummiesRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    uuid: str
    name: str
    description: str | None = None
