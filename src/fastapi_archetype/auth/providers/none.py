from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError, AuthProvider
from fastapi_archetype.auth.models import Principal


class NoAuthProvider(AuthProvider):
    name = "none"

    async def authenticate_bearer_token(self, token: str) -> Principal:
        _ = token
        return Principal(
            subject="auth-disabled",
            user_id="auth-disabled",
            name="Auth Disabled",
            scope="*",
            app_id="none",
            roles=["admin", "writer", "reader"],
            groups=[],
            claims={"auth_type": "none"},
        )

    async def get_client_credentials_access_token(self, scope: str) -> str:
        _ = scope
        raise AuthFeatureNotSupportedError(
            "Token management is unavailable with AUTH_TYPE=none"
        )

    async def get_on_behalf_of_access_token(self, scope: str, user_token: str) -> str:
        _ = (scope, user_token)
        raise AuthFeatureNotSupportedError(
            "OBO flow is unavailable with AUTH_TYPE=none"
        )
