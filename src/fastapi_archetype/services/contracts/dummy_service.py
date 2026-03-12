from abc import ABC, abstractmethod

from sqlmodel import Session

from fastapi_archetype.models.entities.dummy import Dummy


class DummyServiceV1Contract(ABC):
    @abstractmethod
    def get_all_dummies(self, session: Session) -> list[Dummy]: ...

    @abstractmethod
    def get_dummy_by_uuid(self, session: Session, uuid: str) -> Dummy | None: ...

    @abstractmethod
    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy: ...

    @abstractmethod
    def update_dummy(self, session: Session, entity: Dummy) -> Dummy: ...


class DummyServiceV2Contract(ABC):
    @abstractmethod
    def get_all_dummies(self, session: Session) -> list[Dummy]: ...

    @abstractmethod
    def create_dummy(self, session: Session, dummy: Dummy) -> Dummy: ...
