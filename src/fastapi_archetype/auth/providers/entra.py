from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import httpx
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

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
            claims = jwt.get_unverified_claims(token)
        except JWTError as exc:
            raise UnauthorizedError("Malformed bearer token") from exc

        jwks = await self._get_jwks()
        key = self._select_signing_key(jwks, header.get("kid"))
        self._verify_signature(token, key, header.get("alg"))
        self._validate_standard_claims(claims)
        return self._principal_from_claims(claims)

    async def get_client_credentials_access_token(self, scope: str) -> str:
        form = {
            "client_id": self._settings.auth_external_client_id,
            "client_secret": self._settings.auth_external_client_secret,
            "grant_type": "client_credentials",
        }
        if scope:
            form["scope"] = scope
        return await self._request_access_token(form)

    async def get_on_behalf_of_access_token(self, scope: str, user_token: str) -> str:
        form = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self._settings.auth_external_client_id,
            "client_secret": self._settings.auth_external_client_secret,
            "assertion": user_token,
            "scope": scope,
            "requested_token_use": "on_behalf_of",
        }
        return await self._request_access_token(form)

    async def get_current_user_roles(
        self,
        principal: Principal,
        user_token: str,
    ) -> list[str]:
        return await self.get_user_roles(principal.user_id, user_token)

    async def get_user_roles(self, user_id: str, user_token: str) -> list[str]:
        obo_token = await self.get_on_behalf_of_access_token(
            self._settings.auth_external_graph_scope,
            user_token,
        )
        uri = self._settings.auth_external_graph_roles_uri_template.format(
            user_id=user_id
        )
        body = await self._http_get(uri, {"Authorization": f"Bearer {obo_token}"})
        values = body.get("value", []) if isinstance(body, dict) else []
        if not isinstance(values, list):
            return []
        normalized_roles: list[str] = []
        for item in values:
            if not isinstance(item, dict):
                continue
            app_role_id = item.get("appRoleId")
            if isinstance(app_role_id, str) and app_role_id:
                normalized_roles.append(app_role_id)
        return normalized_roles

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

    def _select_signing_key(
        self,
        jwks_payload: dict[str, Any],
        kid: Any,
    ) -> dict[str, Any]:
        keys = jwks_payload.get("keys", [])
        if not isinstance(keys, list):
            raise UnauthorizedError("Invalid JWKS payload")
        for key in keys:
            if isinstance(key, dict) and kid and key.get("kid") == kid:
                return key
        for key in keys:
            if isinstance(key, dict):
                return key
        raise UnauthorizedError("No signing key available in JWKS")

    def _verify_signature(
        self,
        token: str,
        signing_key: dict[str, Any],
        alg: Any,
    ) -> None:
        if not isinstance(alg, str):
            raise UnauthorizedError("Missing token algorithm")
        message, encoded_signature = token.rsplit(".", 1)
        decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
        key = jwk.construct(signing_key, algorithm=alg)
        if not key.verify(message.encode("utf-8"), decoded_signature):
            raise UnauthorizedError("Invalid token signature")

    def _validate_standard_claims(self, claims: dict[str, Any]) -> None:
        now_ts = int(datetime.now(UTC).timestamp())
        exp = claims.get("exp")
        if isinstance(exp, int) and exp < now_ts:
            raise UnauthorizedError("Token has expired")
        nbf = claims.get("nbf")
        if isinstance(nbf, int) and nbf > now_ts:
            raise UnauthorizedError("Token not yet valid")
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

    def _principal_from_claims(self, claims: dict[str, Any]) -> Principal:
        raw_roles = claims.get("roles", [])
        raw_groups = claims.get("groups", [])
        return Principal(
            subject=str(claims.get("sub", "")),
            user_id=str(claims.get("oid", claims.get("sub", ""))),
            name=str(claims["name"]) if "name" in claims else None,
            scope=str(claims["scp"]) if "scp" in claims else None,
            app_id=str(claims["appid"]) if "appid" in claims else None,
            roles=(
                [str(role) for role in raw_roles]
                if isinstance(raw_roles, list)
                else []
            ),
            groups=[
                str(group) for group in raw_groups
            ] if isinstance(raw_groups, list) else [],
            claims=claims,
        )
