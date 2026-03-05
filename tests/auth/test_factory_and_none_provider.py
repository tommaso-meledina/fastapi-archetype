from __future__ import annotations

import builtins
import sys

import pytest

from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.auth.models import Principal
from fastapi_archetype.auth.providers.none import NoAuthProvider
from fastapi_archetype.core.config import AppSettings


def _entra_settings() -> AppSettings:
    return AppSettings(
        auth_type="entra",
        auth_external_issuer="https://issuer.example.test",
        auth_external_jwks_uri="https://issuer.example.test/keys",
        auth_external_token_uri="https://issuer.example.test/token",
        auth_external_client_id="client-id",
        auth_external_client_secret="client-secret",
    )


def test_build_auth_facade_uses_entra_provider() -> None:
    facade = build_auth_facade(_entra_settings())
    assert facade.provider_name == "external-entra"


def test_build_auth_facade_errors_when_httpx_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(
        sys.modules,
        "fastapi_archetype.auth.providers.entra",
        raising=False,
    )
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fastapi_archetype.auth.providers.entra":
            raise ModuleNotFoundError("No module named 'httpx'", name="httpx")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    with pytest.raises(RuntimeError, match="AUTH_TYPE=entra requires httpx"):
        build_auth_facade(_entra_settings())


@pytest.mark.anyio
async def test_no_auth_provider_obo_not_supported() -> None:
    provider = NoAuthProvider()
    with pytest.raises(AuthFeatureNotSupportedError, match="OBO flow is unavailable"):
        await provider.get_on_behalf_of_access_token("scope", "user-token")


@pytest.mark.anyio
async def test_no_auth_provider_current_user_roles_returns_principal_roles() -> None:
    provider = NoAuthProvider()
    principal = Principal(
        subject="subject-1",
        user_id="user-1",
        name="User",
        scope="*",
        app_id="none",
        roles=["reader", "writer"],
        groups=[],
        claims={},
    )

    roles = await provider.get_current_user_roles(principal, "ignored-token")
    assert roles == ["reader", "writer"]


@pytest.mark.anyio
async def test_no_auth_provider_user_role_lookup_not_supported() -> None:
    provider = NoAuthProvider()
    with pytest.raises(
        AuthFeatureNotSupportedError,
        match="Role lookup is unavailable with AUTH_TYPE=none",
    ):
        await provider.get_user_roles("user-1", "user-token")
