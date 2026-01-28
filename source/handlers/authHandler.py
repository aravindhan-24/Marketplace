import logging
from fastapi import Request, HTTPException, status
import base64
import jwt
from datetime import datetime, timezone, timedelta

from source.constants.constants import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)


def createJWTToken(userId: int):
    logger.info(f"Creating JWT token for user_id={userId}")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(userId),
        "iat": now,
        "exp": now + timedelta(hours=1),
        "scope": ["READ", "WRITE"],
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"JWT token verified successfully for sub={decoded_data.get('sub')}")
        return decoded_data

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token verification failed: token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        logger.warning("JWT token verification failed: invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def getToken(request: Request):
    authHeader = request.headers.get("Authorization")

    if not authHeader:
        logger.warning("Authorization header missing in Basic auth request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    authArr = authHeader.split(" ")

    if len(authArr) != 2 or authArr[0] != "Basic":
        logger.warning("Invalid Authorization header format for Basic auth")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )

    credentialsStr = base64.b64decode(authArr[1]).decode("utf-8")
    credentialsArr = credentialsStr.split(":")

    # In production: password must be hashed & checked against DB
    if credentialsArr[0] == "admin" and credentialsArr[1] == "Admin@123":
        logger.info("Basic authentication successful for user=admin")
        return {"creadentials": createJWTToken(10001)}

    logger.warning("Basic authentication failed: invalid credentials")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
