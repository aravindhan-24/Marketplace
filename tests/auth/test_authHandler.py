import base64
import jwt
from datetime import datetime, timezone, timedelta

import pytest
from fastapi import HTTPException

from source.handlers.authHandler import createJWTToken, verify_token, getToken
from source.constants import SECRET_KEY, ALGORITHM

class DummyRequest:
    def __init__(self, headers: dict):
        self.headers = headers


def test_createJWTToken_returns_valid_jwt():
    token = createJWTToken(10001)

    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "10001"
    assert "iat" in decoded
    assert "exp" in decoded
    assert decoded["scope"] == ["READ", "WRITE"]


def test_verify_token_valid_token():
    token = createJWTToken(20002)
    decoded = verify_token(token)

    assert decoded["sub"] == "20002"


def test_verify_token_invalid_token():
    decoded = verify_token("fake.token.value")
    assert decoded == "Invalid token!"


def test_verify_token_expired_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "12345",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "scope": ["READ", "WRITE"],
    }

    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    decoded = verify_token(expired_token)
    assert decoded == "Token has expired!"


def test_getToken_valid_basic_auth_returns_token():
    creds = "admin:Admin@123"
    encoded = base64.b64encode(creds.encode()).decode()

    request = DummyRequest(headers={"Authorization": f"Basic {encoded}"})

    result = getToken(request)

    assert "creadentials" in result
    token = result["creadentials"]

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "10001"


def test_getToken_invalid_basic_auth_raises_401():
    creds = "admin:wrongpass"
    encoded = base64.b64encode(creds.encode()).decode()

    request = DummyRequest(headers={"Authorization": f"Basic {encoded}"})

    with pytest.raises(HTTPException) as exc:
        getToken(request)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
