from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_archetype.auth.contracts import AuthProvider
    from fastapi_archetype.auth.models import Principal


class AuthFacade:
    """Facade that keeps provider-specific auth logic behind one boundary."""

    def __init__(
        self,
        primary_provider: AuthProvider,
    ) -> None:
        self._primary_provider = primary_provider

    @property
    def provider_name(self) -> str:
        return self._primary_provider.name

    async def authenticate_bearer_token(self, token: str) -> Principal:
        return await self._primary_provider.authenticate_bearer_token(token)

    async def get_client_credentials_access_token(self, scope: str) -> str:
        return await self._primary_provider.get_client_credentials_access_token(scope)

    async def get_on_behalf_of_access_token(self, scope: str, user_token: str) -> str:
        return await self._primary_provider.get_on_behalf_of_access_token(
            scope,
            user_token,
        )

    async def get_current_user_roles(
        self,
        principal: Principal,
        user_token: str,
    ) -> list[str]:
        return await self._primary_provider.get_current_user_roles(
            principal,
            user_token,
        )

    async def get_user_roles(self, user_id: str, user_token: str) -> list[str]:
        return await self._primary_provider.get_user_roles(user_id, user_token)
