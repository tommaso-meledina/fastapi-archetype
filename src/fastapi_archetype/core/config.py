import os
import warnings
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
VALID_LOG_MODES = frozenset({"plain", "json"})
VALID_PROFILES = frozenset({"default", "mock"})


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env") or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "fastapi-archetype"
    debug: bool = False
    log_level: str = "INFO"
    log_mode: str = "plain"
    profile: Literal["default", "mock"] = "default"

    @field_validator("profile", mode="before")
    @classmethod
    def _normalize_profile(cls, value: object) -> str:
        s = str(value).lower() if value is not None else "default"
        if s not in VALID_PROFILES:
            allowed = ", ".join(sorted(VALID_PROFILES))
            msg = f"Invalid profile '{value}'. Must be one of: {allowed}"
            raise ValueError(msg)
        return s

    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        upper = value.upper()
        if upper not in VALID_LOG_LEVELS:
            allowed = ", ".join(sorted(VALID_LOG_LEVELS))
            msg = f"Invalid log level '{value}'. Must be one of: {allowed}"
            raise ValueError(msg)
        return upper

    @field_validator("log_mode")
    @classmethod
    def _normalize_log_mode(cls, value: str) -> str:
        lower = value.lower()
        if lower not in VALID_LOG_MODES:
            warnings.warn(
                f"Invalid LOG_MODE '{value}', falling back to 'plain'",
                stacklevel=2,
            )
            return "plain"
        return lower

    otel_export_enabled: bool = False
    otel_exporter_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "fastapi-archetype"

    root_path: str = ""
    cors_enabled: bool = False
    cors_allow_origins: str = ""
    cors_allow_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_allow_headers: str = "Authorization,Content-Type"
    cors_allow_credentials: bool = False
    cors_expose_headers: str = ""

    rate_limit_get_dummies: str = "100/minute"
    rate_limit_post_dummies: str = "10/minute"

    database_url: str | None = None

    auth_type: Literal["none", "entra"] = "none"
    auth_external_issuer: str = ""
    auth_external_audience: str = ""
    auth_external_discovery_uri: str = ""
    auth_external_jwks_uri: str = ""
    auth_external_token_uri: str = ""
    auth_external_client_id: str = ""
    auth_external_client_secret: str = ""

    auth_http_timeout_seconds: float = 10.0
    auth_http_retry_attempts: int = 1

    @model_validator(mode="after")
    def _validate_external_auth_requirements(self) -> AppSettings:
        if self.auth_type != "entra":
            pass
        else:
            missing_fields: list[str] = []
            if not self.auth_external_issuer.strip():
                missing_fields.append("AUTH_EXTERNAL_ISSUER")
            if (
                not self.auth_external_discovery_uri.strip()
                and not self.auth_external_jwks_uri.strip()
            ):
                missing_fields.append(
                    "AUTH_EXTERNAL_DISCOVERY_URI or AUTH_EXTERNAL_JWKS_URI"
                )
            if missing_fields:
                missing = ", ".join(missing_fields)
                msg = f"AUTH_TYPE=entra requires the following settings: {missing}"
                raise ValueError(msg)

        if self.cors_allow_credentials and "*" in self.cors_allow_origins_list:
            msg = (
                "CORS_ALLOW_ORIGINS cannot include '*' when CORS_ALLOW_CREDENTIALS=true"
            )
            raise ValueError(msg)
        return self

    @staticmethod
    def _parse_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return self._parse_csv(self.cors_allow_origins)

    @property
    def cors_allow_methods_list(self) -> list[str]:
        return self._parse_csv(self.cors_allow_methods)

    @property
    def cors_allow_headers_list(self) -> list[str]:
        return self._parse_csv(self.cors_allow_headers)

    @property
    def cors_expose_headers_list(self) -> list[str]:
        return self._parse_csv(self.cors_expose_headers)

    @property
    def effective_database_url(self) -> str:
        """URL used for engine creation. Unset or empty/whitespace → sqlite://."""
        raw = self.database_url
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            return "sqlite://"
        return raw.strip()
