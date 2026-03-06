from __future__ import annotations

import builtins
import sys

import pytest

from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError
from fastapi_archetype.auth.factory import build_auth_facade
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


