from fastapi_archetype.models.dto import CamelCaseModel


class PostDummiesRequest(CamelCaseModel):
    name: str
    description: str | None = None


class GetDummiesResponse(CamelCaseModel):
    uuid: str
    name: str
    name_initial: str
    description: str | None = None


class PostDummiesResponse(CamelCaseModel):
    uuid: str
    name: str
    description: str | None = None


class PutDummiesRequest(CamelCaseModel):
    uuid: str
    name: str
    description: str | None = None
