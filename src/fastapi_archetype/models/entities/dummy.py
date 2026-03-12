import uuid as uuid_module

from sqlmodel import Field, SQLModel


class Dummy(SQLModel, table=True):
    __tablename__ = "DUMMY"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(
        default_factory=lambda: str(uuid_module.uuid4()), unique=True, index=True
    )
    name: str
    description: str | None = None
