from __future__ import annotations

import uuid as uuid_module

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


def _to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _default_uuid() -> str:
    return str(uuid_module.uuid4())


class Dummy(SQLModel, table=True):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

    __tablename__ = "DUMMY"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=_default_uuid, unique=True, index=True)
    name: str
    description: str | None = None
