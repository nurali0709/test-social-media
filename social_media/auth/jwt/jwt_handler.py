import jwt
import time

from social_media.config import JWT_ALGORITHM, JWT_SECRET

def token_response(token: str):
    return {
        "access token": token
    }

def JWT_sign(username: str):
    payload = {
        "username": username,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def JWT_decode(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token['expires'] >= time.time() else None
    except:
        return {}
