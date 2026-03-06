from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import httpx
import jwt
from jwt import PyJWK

from fastapi_archetype.auth.contracts import (
    AuthFeatureNotSupportedError,
    AuthProvider,
    UnauthorizedError,
)
from fastapi_archetype.auth.models import Principal

if TYPE_CHECKING:
    from fastapi_archetype.core.config import AppSettings


class EntraExternalAuthProvider(AuthProvider):
    name = "external-entra"

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_until = datetime.min.replace(tzinfo=UTC)
        self._jwks_cache_ttl_seconds = 300

    async def authenticate_bearer_token(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Malformed bearer token") from exc

        alg = header.get("alg")
        if not isinstance(alg, str):
            raise UnauthorizedError("Missing token algorithm")

        jwks = await self._get_jwks()
        signing_key = self._select_signing_key(jwks, header.get("kid"))
        self._validate_signing_key_metadata(signing_key, alg)
        claims = self._decode_and_verify(token, signing_key, alg)
        self._validate_issuer_and_audience(claims)
        return self._principal_from_claims(claims)

    async def get_client_credentials_access_token(self, scope: str) -> str:
        self._require_client_credentials()
        form = {
            "client_id": self._settings.auth_external_client_id,
            "client_secret": self._settings.auth_external_client_secret,
            "grant_type": "client_credentials",
        }
        if scope:
            form["scope"] = scope
        return await self._request_access_token(form)

    async def get_on_behalf_of_access_token(self, scope: str, user_token: str) -> str:
        self._require_client_credentials()
        form = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self._settings.auth_external_client_id,
            "client_secret": self._settings.auth_external_client_secret,
            "assertion": user_token,
            "scope": scope,
            "requested_token_use": "on_behalf_of",
        }
        return await self._request_access_token(form)

    def _require_client_credentials(self) -> None:
        missing: list[str] = []
        if not self._settings.auth_external_client_id.strip():
            missing.append("auth_external_client_id")
        if not self._settings.auth_external_client_secret.strip():
            missing.append("auth_external_client_secret")
        if missing:
            raise AuthFeatureNotSupportedError(
                f"{', '.join(missing)} must be configured for this operation"
            )

    async def _request_access_token(self, form: dict[str, str]) -> str:
        if not self._settings.auth_external_token_uri:
            raise AuthFeatureNotSupportedError(
                "auth_external_token_uri is not configured"
            )
        body = await self._http_post_form(self._settings.auth_external_token_uri, form)
        token = body.get("access_token") if isinstance(body, dict) else None
        if not isinstance(token, str) or not token:
            raise UnauthorizedError("Token endpoint response missing access_token")
        return token

    async def _get_jwks(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        if self._jwks_cache is not None and now < self._jwks_cache_until:
            return self._jwks_cache

        jwks_uri = await self._resolve_jwks_uri()
        payload = await self._http_get(jwks_uri)
        keys = payload.get("keys") if isinstance(payload, dict) else None
        if not isinstance(keys, list):
            msg = "JWKS endpoint did not return a valid keys list"
            raise UnauthorizedError(msg)
        self._jwks_cache = payload
        self._jwks_cache_until = now + timedelta(seconds=self._jwks_cache_ttl_seconds)
        return payload

    async def _resolve_jwks_uri(self) -> str:
        if self._settings.auth_external_jwks_uri:
            return self._settings.auth_external_jwks_uri
        if not self._settings.auth_external_discovery_uri:
            msg = (
                "Either auth_external_jwks_uri or auth_external_discovery_uri "
                "is required"
            )
            raise UnauthorizedError(msg)
        discovery = await self._http_get(self._settings.auth_external_discovery_uri)
        jwks_uri = discovery.get("jwks_uri") if isinstance(discovery, dict) else None
        if not isinstance(jwks_uri, str) or not jwks_uri:
            raise UnauthorizedError("Discovery document missing jwks_uri")
        return jwks_uri

    async def _http_get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        attempts = max(1, self._settings.auth_http_retry_attempts)
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                async with httpx.AsyncClient(
                    timeout=self._settings.auth_http_timeout_seconds
                ) as client:
                    response = await client.get(url, headers=headers)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    return payload
                raise UnauthorizedError("Expected JSON object payload")
            except (httpx.HTTPError, ValueError, UnauthorizedError) as exc:
                last_error = exc
        raise UnauthorizedError("HTTP GET request failed") from last_error

    async def _http_post_form(self, url: str, data: dict[str, str]) -> dict[str, Any]:
        attempts = max(1, self._settings.auth_http_retry_attempts)
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                async with httpx.AsyncClient(
                    timeout=self._settings.auth_http_timeout_seconds
                ) as client:
                    response = await client.post(url, data=data)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    return payload
                raise UnauthorizedError("Expected JSON object payload")
            except (httpx.HTTPError, ValueError, UnauthorizedError) as exc:
                last_error = exc
        raise UnauthorizedError("HTTP POST request failed") from last_error

    @staticmethod
    def _select_signing_key(
        jwks_payload: dict[str, Any],
        kid: Any,
    ) -> dict[str, Any]:
        keys = jwks_payload.get("keys", [])
        if not isinstance(keys, list):
            raise UnauthorizedError("Invalid JWKS payload")
        for key in keys:
            if isinstance(key, dict) and kid and key.get("kid") == kid:
                return key
        if kid:
            raise UnauthorizedError(f"No signing key found for token kid={kid}")
        for key in keys:
            if isinstance(key, dict):
                return key
        raise UnauthorizedError("No signing key available in JWKS")

    @staticmethod
    def _validate_signing_key_metadata(
        signing_key: dict[str, Any],
        alg: str,
    ) -> None:
        key_type = signing_key.get("kty")
        key_use = signing_key.get("use")
        if alg.startswith("RS") and key_type != "RSA":
            raise UnauthorizedError(
                f"Signing key type mismatch: alg={alg}, key.kty={key_type}"
            )
        if isinstance(key_use, str) and key_use.lower() != "sig":
            raise UnauthorizedError(f"JWKS key use is not signing: use={key_use}")

    @staticmethod
    def _decode_and_verify(
        token: str,
        signing_key: dict[str, Any],
        alg: str,
    ) -> dict[str, Any]:
        try:
            jwk_data = {**signing_key}
            if "alg" not in jwk_data:
                jwk_data["alg"] = alg
            key = PyJWK(jwk_data).key
            return jwt.decode(
                token,
                key=key,
                algorithms=[alg],
                options={"verify_iss": False, "verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise UnauthorizedError("Token has expired") from exc
        except jwt.ImmatureSignatureError as exc:
            raise UnauthorizedError("Token not yet valid") from exc
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Invalid token signature") from exc

    def _validate_issuer_and_audience(self, claims: dict[str, Any]) -> None:
        iss = claims.get("iss")
        if (
            self._settings.auth_external_issuer
            and iss != self._settings.auth_external_issuer
        ):
            raise UnauthorizedError("Invalid token issuer")
        required_audience = self._settings.auth_external_audience
        if not required_audience:
            return
        aud = claims.get("aud")
        if isinstance(aud, str) and aud == required_audience:
            return
        if isinstance(aud, list) and required_audience in aud:
            return
        raise UnauthorizedError("Invalid token audience")

    @staticmethod
    def _principal_from_claims(claims: dict[str, Any]) -> Principal:
        raw_roles = claims.get("roles", [])
        raw_groups = claims.get("groups", [])
        return Principal(
            subject=str(claims.get("sub", "")),
            user_id=str(claims.get("oid", claims.get("sub", ""))),
            name=str(claims["name"]) if "name" in claims else None,
            scope=str(claims["scp"]) if "scp" in claims else None,
            app_id=str(claims["appid"]) if "appid" in claims else None,
            roles=(
                [str(role) for role in raw_roles] if isinstance(raw_roles, list) else []
            ),
            groups=[str(group) for group in raw_groups]
            if isinstance(raw_groups, list)
            else [],
            claims=claims,
        )
