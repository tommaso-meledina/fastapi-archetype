from __future__ import annotations

import pytest

from fastapi_archetype.auth.contracts import AuthFeatureNotSupportedError
from fastapi_archetype.auth.factory import build_auth_facade
from fastapi_archetype.core.config import AppSettings


@pytest.mark.anyio
async def test_none_facade_bypasses_bearer_validation() -> None:
    settings = AppSettings(auth_type="none")
    facade = build_auth_facade(settings)
    principal = await facade.authenticate_bearer_token("any-token-or-none")
    assert principal.user_id == "auth-disabled"
    assert "admin" in principal.roles


@pytest.mark.anyio
async def test_none_facade_client_credentials_not_supported() -> None:
    settings = AppSettings(auth_type="none")
    facade = build_auth_facade(settings)
    with pytest.raises(AuthFeatureNotSupportedError):
        await facade.get_client_credentials_access_token("scope")
