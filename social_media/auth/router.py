import bcrypt
import uuid
import jwt

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from .models import User, Post
from .schemas import UserSignup, UserLogin, PostCreate
from social_media.database import async_session_maker
from jwt import PyJWTError
from social_media.config import JWT_ALGORITHM, JWT_SECRET

from .jwt.jwt_handler import JWT_sign, JWT_decode, verify_token
from .jwt.jwt_bearer import jwt_bearer

router = APIRouter(
    prefix="/auth",
    tags = ["Auth"]
)

@router.post("/signup")
async def signup(user: UserSignup):
    async with async_session_maker() as session:
        try:
            db_user = await session.execute(select(User).where(User.username == user.username))
            if db_user.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already exists")
        except NoResultFound:
            pass

        # Hash the password for security
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Save the user in the database
        db_user = User(username=user.username, password=hashed_password.decode("utf-8"))
        session.add(db_user)
        await session.commit()

        # Generate JWT token upon successful signup
        token = JWT_sign(user.username)

        return {"jwt": token}

@router.post("/login")
async def login(user: UserLogin):
    async with async_session_maker() as session:
        db_user = await session.execute(select(User).where(User.username == user.username))
        user_obj = db_user.scalar_one_or_none()

        if not user_obj or not bcrypt.checkpw(user.password.encode("utf-8"), user_obj.password.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Generate a JWT token
        token = JWT_sign(user.username)

        return {"jwt": token}

@router.post("/create_post")
async def create_post(post: PostCreate, token: str = Depends(jwt_bearer())):
    # Token verification has already been handled by the JWTBearer dependency
    # You can extract the username from the token payload and proceed with creating the post

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

    # Create the post with the provided data and assign the user's id as the author_id
    new_post = Post(title=post.title, description=post.description, likes=0, dislikes=0, author_id=user_obj.id)

    # Add the post to the session and commit the changes
    async with async_session_maker() as session:
        session.add(new_post)
        await session.commit()

    return {"message": "Post created successfully"}
