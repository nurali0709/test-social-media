'''JWT handling modules'''
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer


class JwtBearer(HTTPBearer):
    '''Authorization with JWT'''

    def __init__(self, auto_Error: bool = True):
        super(JwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        if token:
            return token
        if self.auto_error:
            raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
        return None
