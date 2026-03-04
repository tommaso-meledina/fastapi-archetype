from __future__ import annotations

import pytest
from pydantic import ValidationError

from fastapi_archetype.core.config import AppSettings


def test_default_settings_load(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("DB_DRIVER", "sqlite")
    monkeypatch.delenv("DEBUG", raising=False)
    settings = AppSettings()
    assert settings.app_name == "fastapi-archetype"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.db_driver == "sqlite"


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_valid_log_levels(monkeypatch: pytest.MonkeyPatch, level: str) -> None:
    monkeypatch.setenv("LOG_LEVEL", level)
    settings = AppSettings()
    assert settings.log_level == level


def test_log_level_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")
    settings = AppSettings()
    assert settings.log_level == "DEBUG"


def test_invalid_log_level_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "INVALID")
    with pytest.raises(ValidationError, match="Invalid log level"):
        AppSettings()


def test_root_path_defaults_to_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ROOT_PATH", raising=False)
    settings = AppSettings()
    assert settings.root_path == ""


def test_root_path_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROOT_PATH", "/api/v1")
    settings = AppSettings()
    assert settings.root_path == "/api/v1"


def test_database_url_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_DRIVER", "sqlite")
    settings = AppSettings()
    assert settings.database_url == "sqlite://"


def test_database_url_mysql(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_DRIVER", "mysql+pymysql")
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    monkeypatch.setenv("DB_HOST", "dbhost")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_NAME", "testdb")
    settings = AppSettings()
    assert (
        settings.database_url == "mysql+pymysql://testuser:testpass@dbhost:3307/testdb"
    )


def test_entra_auth_requires_external_settings() -> None:
    with pytest.raises(ValidationError, match="AUTH_TYPE=entra requires"):
        AppSettings(auth_type="entra")


def test_entra_auth_accepts_required_settings() -> None:
    settings = AppSettings(
        auth_type="entra",
        auth_external_issuer="https://issuer.example.test",
        auth_external_discovery_uri="https://issuer.example.test/.well-known/openid-configuration",
        auth_external_token_uri="https://issuer.example.test/oauth2/v2.0/token",
        auth_external_client_id="client-id",
        auth_external_client_secret="client-secret",
    )
    assert settings.auth_type == "entra"
