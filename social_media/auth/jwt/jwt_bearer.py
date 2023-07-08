from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import JWT_decode

class jwt_bearer(HTTPBearer):
    def __init__(self, auto_Error : bool = True):
        super(jwt_bearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request : Request):
        credentials: HTTPAuthorizationCredentials = await super(jwt_bearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code = 403, details="Invalid or Expired Token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, details="Invalid or Expired Token")

    def verify_jwt(self, jwtoken: str):
        is_token_valid: bool = False
        payload = JWT_decode(jwtoken)
        if payload:
            is_token_valid = True

