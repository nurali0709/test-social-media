import jwt
from datetime import datetime, timedelta

from social_media.config import JWT_SECRET

def generate_token(username: str, token_id: str) -> str:
    # Define the token expiration time
    expiration = datetime.utcnow() + timedelta(hours=24)

    # Create the token payload
    payload = {"username": username, "token_id": token_id, "exp": expiration}

    # Generate the token
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return token
