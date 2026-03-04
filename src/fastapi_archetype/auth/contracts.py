from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_archetype.auth.models import Principal


class AuthError(Exception):
    """Base error for auth/authz subsystem failures."""


class UnauthorizedError(AuthError):
    """Raised when token authentication fails."""


class ForbiddenError(AuthError):
    """Raised when authn succeeds but authz fails."""


class AuthFeatureNotSupportedError(AuthError):
    """Raised when provider cannot fulfill requested capability."""


class RoleMappingProvider(ABC):
    """Maps internal role labels to external identifiers (e.g. GUIDs)."""

    @abstractmethod
    def to_external(self, role_name: str) -> str: ...


class AuthProvider(ABC):
    name: str

    @abstractmethod
    async def authenticate_bearer_token(self, token: str) -> Principal: ...

    @abstractmethod
    async def get_client_credentials_access_token(self, scope: str) -> str: ...

    @abstractmethod
    async def get_on_behalf_of_access_token(
        self,
        scope: str,
        user_token: str,
    ) -> str: ...

    @abstractmethod
    async def get_current_user_roles(
        self,
        principal: Principal,
        user_token: str,
    ) -> list[str]: ...

    @abstractmethod
    async def get_user_roles(self, user_id: str, user_token: str) -> list[str]: ...
