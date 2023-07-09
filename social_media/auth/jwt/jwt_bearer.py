'''JWT handling modules'''
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JwtBearer(HTTPBearer):
    '''Authorization with JWT'''
    def __init__(self, auto_Error : bool = True):
        super(JwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request : Request):
        credentials: HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code = 403)
            return credentials.credentials
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
