from __future__ import annotations

import pytest

from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError
from fastapi_archetype.auth.providers.entra import EntraExternalAuthProvider
from fastapi_archetype.core.config import AppSettings


@pytest.mark.anyio
async def test_external_provider_client_credentials_uses_token_endpoint() -> None:
    settings = AppSettings(
        auth_type="entra",
        auth_external_issuer="https://issuer.example.test",
        auth_external_jwks_uri="https://issuer.example.test/keys",
        auth_external_token_uri="https://example.test/token",
        auth_external_client_id="client-id",
        auth_external_client_secret="client-secret",
    )
    provider = EntraExternalAuthProvider(settings)

    async def _fake_post(url: str, data: dict[str, str]) -> dict[str, str]:
        assert url == "https://example.test/token"
        assert data["grant_type"] == "client_credentials"
        return {"access_token": "cc-token"}

    provider._http_post_form = _fake_post  # type: ignore[method-assign]
    token = await provider.get_client_credentials_access_token("scope://api/.default")
    assert token == "cc-token"


@pytest.mark.anyio
async def test_external_provider_user_roles_normalized_to_app_role_id() -> None:
    settings = AppSettings(
        auth_type="entra",
        auth_external_issuer="https://issuer.example.test",
        auth_external_jwks_uri="https://issuer.example.test/keys",
        auth_external_token_uri="https://example.test/token",
        auth_external_client_id="client-id",
        auth_external_client_secret="client-secret",
        auth_external_graph_roles_uri_template=(
            "https://graph.example.test/users/{user_id}/appRoleAssignments"
        ),
    )
    provider = EntraExternalAuthProvider(settings)

    async def _fake_obo(scope: str, user_token: str) -> str:
        return "obo-token"

    async def _fake_get(
        url: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        assert "user-1" in url
        assert headers == {"Authorization": "Bearer obo-token"}
        return {
            "value": [
                {"appRoleId": "role-1", "resourceDisplayName": "Reader"},
                {"appRoleId": "role-2", "resourceDisplayName": "Writer"},
            ]
        }

    provider.get_on_behalf_of_access_token = _fake_obo  # type: ignore[method-assign]
    provider._http_get = _fake_get  # type: ignore[method-assign]
    roles = await provider.get_user_roles("user-1", "subject-token")
    assert roles == ["role-1", "role-2"]


def _settings_without_client_secret() -> AppSettings:
    return AppSettings(
        auth_type="entra",
        auth_external_issuer="https://issuer.example.test",
        auth_external_jwks_uri="https://issuer.example.test/keys",
        auth_external_token_uri="https://example.test/token",
        auth_external_client_id="client-id",
    )


@pytest.mark.anyio
async def test_client_credentials_raises_when_no_client_secret() -> None:
    provider = EntraExternalAuthProvider(_settings_without_client_secret())
    with pytest.raises(AuthFeatureNotSupportedError, match="client_secret"):
        await provider.get_client_credentials_access_token("scope://api/.default")


@pytest.mark.anyio
async def test_obo_raises_when_no_client_secret() -> None:
    provider = EntraExternalAuthProvider(_settings_without_client_secret())
    with pytest.raises(AuthFeatureNotSupportedError, match="client_secret"):
        await provider.get_on_behalf_of_access_token("scope://api/.default", "token")
