import builtins

import pytest

from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.core.config import AppSettings


@pytest.mark.asyncio
async def test_none_facade_bypasses_bearer_validation() -> None:
    settings = AppSettings(auth_type="none")
    facade = build_auth_facade(settings)
    principal = await facade.authenticate_bearer_token("any-token-or-none")
    assert principal.user_id == "auth-disabled"
    assert "admin" in principal.roles


@pytest.mark.asyncio
async def test_none_facade_client_credentials_not_supported() -> None:
    settings = AppSettings(auth_type="none")
    facade = build_auth_facade(settings)
    with pytest.raises(AuthFeatureNotSupportedError):
        await facade.get_client_credentials_access_token("scope")


def test_none_facade_does_not_import_entra_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import = builtins.__import__

    def guarded_import(name, globals_=None, locals_=None, fromlist=(), level=0):
        if name == "fastapi_archetype.auth.providers.entra":
            msg = "Entra provider import must not happen with AUTH_TYPE=none"
            raise AssertionError(msg)
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    settings = AppSettings(auth_type="none")
    facade = build_auth_facade(settings)
    assert facade.provider_name == "none"
