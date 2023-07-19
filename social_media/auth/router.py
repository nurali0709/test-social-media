'''Handling Authentication'''
import bcrypt

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from social_media.database import async_session_maker
from .models import User
from .schemas import UserSignup, UserLogin

from .jwt.jwt_handler import jwt_sign

router = APIRouter(
    prefix="/auth",
    tags = ["Auth"]
)

@router.post("/signup")
async def signup(user: UserSignup):
    '''Signing up user with JWT'''
    async with async_session_maker() as session:
        try:
            db_user = await session.execute(select(User).where(User.username == user.username))
            if db_user.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already exists")

            db_email = await session.execute(select(User).where(User.email == user.email))
            if db_email.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already exists")

        except NoResultFound:
            pass

        # Hash the password for security
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Save the user in the database
        db_user = User(username=user.username, password=hashed_password.decode("utf-8"),
                       email=user.email, name=user.name, surname=user.surname)
        session.add(db_user)
        await session.commit()

        # Generate JWT token upon successful signup
        token = jwt_sign(user.username)

        return {"jwt": token}

@router.post("/login")
async def login(user: UserLogin):
    '''Login user with JWT'''
    async with async_session_maker() as session:
        db_user = await session.execute(select(User).where(User.username == user.username))
        user_obj = db_user.scalar_one_or_none()

        if not user_obj or not bcrypt.checkpw(user.password.encode("utf-8"), user_obj.password.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Generate a JWT token
        token = jwt_sign(user.username)

        return {"jwt": token}

@router.get("/users/")
async def get_all_users():
    '''Get all users (GET)'''
    async with async_session_maker() as session:
        users = await session.execute(select(User))
        all_users = users.scalars().all()

    # Extract the required data
    formatted_users = []
    for user in all_users:
        formatted_users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "surname": user.surname
        })

    return formatted_users
