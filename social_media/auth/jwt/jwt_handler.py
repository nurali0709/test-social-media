'''Creating JWT authentication'''
import time
import jwt

from fastapi import HTTPException
from jwt import PyJWTError
from social_media.config import JWT_ALGORITHM, JWT_SECRET


def token_response(token: str):
    '''Token Response'''
    return {"access token": token}


def jwt_sign(username: str):
    '''Creating JWT'''
    payload = {"username": username, "expiry": time.time() + 3600}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


async def verify_token(token: str):
    '''Verifying JWT'''
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")
        return username
    except PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
