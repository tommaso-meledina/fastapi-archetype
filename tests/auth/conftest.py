import base64
import time
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_archetype.auth.contracts import UnauthorizedError
from fastapi_archetype.auth.facade import AuthFacade
from fastapi_archetype.auth.models import Principal
from fastapi_archetype.core.database import get_session
from fastapi_archetype.core.rate_limit import limiter
from fastapi_archetype.main import app


def _int_to_base64url(n: int) -> str:
    b = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


TEST_ISSUER = "https://test-issuer.example.com/"
TEST_AUDIENCE = "api://test-audience"
TEST_KID = "test-key-1"


@pytest.fixture(name="rsa_keypair", scope="module")
def rsa_keypair_fixture() -> dict[str, Any]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    pub_numbers = private_key.public_key().public_numbers()
    return {
        "private_pem": private_pem,
        "n": _int_to_base64url(pub_numbers.n),
        "e": _int_to_base64url(pub_numbers.e),
    }


@pytest.fixture(name="jwks_response")
def jwks_response_fixture(rsa_keypair: dict[str, Any]) -> dict[str, Any]:
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": TEST_KID,
                "use": "sig",
                "alg": "RS256",
                "n": rsa_keypair["n"],
                "e": rsa_keypair["e"],
            }
        ]
    }


@pytest.fixture(name="sign_jwt")
def sign_jwt_fixture(rsa_keypair: dict[str, Any]):
    def _sign(
        claims: dict[str, Any] | None = None,
        *,
        kid: str = TEST_KID,
        algorithm: str = "RS256",
        private_pem: str | None = None,
    ) -> str:
        now = int(time.time())
        default_claims: dict[str, Any] = {
            "sub": "test-subject",
            "oid": "test-oid-123",
            "iss": TEST_ISSUER,
            "aud": TEST_AUDIENCE,
            "name": "Test User",
            "exp": now + 3600,
            "nbf": now - 60,
            "iat": now,
            "roles": ["admin", "reader"],
        }
        if claims:
            default_claims.update(claims)
        return jwt.encode(
            default_claims,
            private_pem or rsa_keypair["private_pem"],
            algorithm=algorithm,
            headers={"kid": kid},
        )

    return _sign


@pytest.fixture(name="entra_engine", scope="module")
def entra_engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(name="entra_client")
def entra_client_fixture(entra_engine) -> Generator[TestClient]:
    """Client with auth_type patched to 'entra' so auth-error paths execute."""
    from unittest.mock import patch

    def _override_session():
        with Session(entra_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    limiter.reset()

    with (
        patch(
            "fastapi_archetype.auth.dependencies.settings.auth_type",
            "entra",
        ),
        TestClient(app) as c,
    ):
        yield c

    app.dependency_overrides.clear()


def mock_facade_unauthorized() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.side_effect = UnauthorizedError(
        "JWKS endpoint did not return a valid keys list"
    )
    return facade


def mock_facade_unexpected_error() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.side_effect = RuntimeError(
        "https://login.microsoftonline.com/.well-known/openid-configuration"
    )
    return facade


def mock_facade_reader_principal() -> AuthFacade:
    facade = AsyncMock(spec=AuthFacade)
    facade.authenticate_bearer_token.return_value = Principal(
        subject="user-1",
        user_id="user-1",
        name="Test User",
        roles=["reader"],
    )
    return facade
