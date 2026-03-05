import os
import warnings
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
VALID_LOG_MODES = frozenset({"plain", "json"})


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

    rate_limit_get_dummies: str = "100/minute"
    rate_limit_post_dummies: str = "10/minute"

    db_driver: Literal["sqlite", "mysql+pymysql"] = "sqlite"
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "fastapi_archetype"

    auth_type: Literal["none", "entra"] = "none"
    auth_external_issuer: str = ""
    auth_external_audience: str = ""
    auth_external_discovery_uri: str = ""
    auth_external_jwks_uri: str = ""
    auth_external_token_uri: str = ""
    auth_external_client_id: str = ""
    auth_external_client_secret: str = ""
    auth_external_graph_scope: str = "https://graph.microsoft.com/.default"
    auth_external_graph_roles_uri_template: str = (
        "https://graph.microsoft.com/v1.0/users/{user_id}/appRoleAssignments"
    )

    auth_http_timeout_seconds: float = 10.0
    auth_http_retry_attempts: int = 1
    auth_enforce_graph_roles: bool = False

    @model_validator(mode="after")
    def _validate_external_auth_requirements(self) -> AppSettings:
        if self.auth_type != "entra":
            return self

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
        if not self.auth_external_token_uri.strip():
            missing_fields.append("AUTH_EXTERNAL_TOKEN_URI")
        if not self.auth_external_client_id.strip():
            missing_fields.append("AUTH_EXTERNAL_CLIENT_ID")
        if not self.auth_external_client_secret.strip():
            missing_fields.append("AUTH_EXTERNAL_CLIENT_SECRET")

        if missing_fields:
            missing = ", ".join(missing_fields)
            msg = f"AUTH_TYPE=entra requires the following settings: {missing}"
            raise ValueError(msg)
        return self

    @property
    def database_url(self) -> str:
        if self.db_driver == "sqlite":
            return "sqlite://"
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
