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


def _settings_without_m2m(**overrides: str) -> AppSettings:
    defaults: dict[str, str] = {
        "auth_type": "entra",
        "auth_external_issuer": "https://issuer.example.test",
        "auth_external_jwks_uri": "https://issuer.example.test/keys",
    }
    defaults.update(overrides)
    # Test fixture: dict overlay; Pydantic validates at runtime.
    return AppSettings(**defaults)  # type: ignore[call-arg]


@pytest.mark.anyio
async def test_client_credentials_raises_when_no_client_secret() -> None:
    settings = _settings_without_m2m(
        auth_external_token_uri="https://example.test/token",
        auth_external_client_id="client-id",
    )
    provider = EntraExternalAuthProvider(settings)
    with pytest.raises(AuthFeatureNotSupportedError, match="client_secret"):
        await provider.get_client_credentials_access_token("scope://api/.default")


@pytest.mark.anyio
async def test_client_credentials_raises_when_no_client_id() -> None:
    settings = _settings_without_m2m(
        auth_external_token_uri="https://example.test/token",
        auth_external_client_secret="client-secret",
    )
    provider = EntraExternalAuthProvider(settings)
    with pytest.raises(AuthFeatureNotSupportedError, match="client_id"):
        await provider.get_client_credentials_access_token("scope://api/.default")


@pytest.mark.anyio
async def test_obo_raises_when_no_client_secret() -> None:
    settings = _settings_without_m2m(
        auth_external_token_uri="https://example.test/token",
        auth_external_client_id="client-id",
    )
    provider = EntraExternalAuthProvider(settings)
    with pytest.raises(AuthFeatureNotSupportedError, match="client_secret"):
        await provider.get_on_behalf_of_access_token("scope://api/.default", "token")


@pytest.mark.anyio
async def test_obo_raises_when_no_client_id() -> None:
    settings = _settings_without_m2m(
        auth_external_token_uri="https://example.test/token",
        auth_external_client_secret="client-secret",
    )
    provider = EntraExternalAuthProvider(settings)
    with pytest.raises(AuthFeatureNotSupportedError, match="client_id"):
        await provider.get_on_behalf_of_access_token("scope://api/.default", "token")
