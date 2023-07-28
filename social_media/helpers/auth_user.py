'''Retrieving authenticated user'''
from fastapi import HTTPException
from sqlalchemy import select
from social_media.auth.models import User
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.database import async_session_maker


async def get_authenticated_user(token: str) -> User:
    '''Retrieve the authenticated user based on the token'''
    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        return user_obj
