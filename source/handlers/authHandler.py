from fastapi import Request, HTTPException, status
import base64
import jwt
from datetime import datetime, timezone, timedelta

from source.constants import SECRET_KEY, ALGORITHM

def createJWTToken(userId: int):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(userId),
        "iat": now,
        "exp": now+ timedelta(hours=1),
        "scope": ["READ","WRITE"],
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return "Token has expired!"
    except jwt.InvalidTokenError:
        return "Invalid token!"

def getToken(request: Request):
    authHeader = request.headers.get("Authorization")
    authArr = authHeader.split(" ")
    if len(authArr)== 2 and authArr[0] == "Basic":
        credentialsStr = base64.b64decode(authArr[1]).decode("utf-8")
        credentialsArr = credentialsStr.split(":")
        #In production setup this will be hashing and checked with DB password column 
        if credentialsArr[0] == "admin" and credentialsArr[1] == "Admin@123":
            return {"creadentials": createJWTToken(10001)}
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
