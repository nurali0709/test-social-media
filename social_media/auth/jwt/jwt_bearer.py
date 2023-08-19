'''JWT handling modules'''
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer


class JwtBearer(HTTPBearer):
    '''Authorization with JWT'''

    def __init__(self, auto_Error: bool = True):
        super(JwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            # Remove "Bearer " from the token
            token = token[len("Bearer "):]
            return token
        elif token:
            return token
        if self.auto_error:
            raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
        return None

    # # For cookie-based authentication
    # async def __call__(self, request: Request):
    #     token = request.cookies.get("jwt")
    #     if token:
    #         return token
    #     if self.auto_error:
    #         raise HTTPException(
    # status_code=401,
    # detail="Invalid or missing authentication token"
    # )
    #     return None
