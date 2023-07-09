import bcrypt
import uuid
import jwt

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from .models import User, Post, Reaction
from .schemas import UserSignup, UserLogin
from social_media.database import async_session_maker

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
