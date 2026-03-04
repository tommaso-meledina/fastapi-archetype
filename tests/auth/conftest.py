from __future__ import annotations

import base64
import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


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
