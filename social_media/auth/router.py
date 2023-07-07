from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from .models import User
from .schemas import UserSignup, UserLogin
from social_media.database import async_session_maker

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

        # Save the user in the database (you may want to hash the password for security)
        db_user = User(username=user.username, password=user.password)
        session.add(db_user)
        await session.commit()

        return {"message": "Signup successful"}


@router.post("/login")
async def login(user: UserLogin):
    async with async_session_maker() as session:
        db_user = await session.execute(selectinload(User).filter(User.username == user.username).first())
        if not db_user or db_user.password != user.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # You can generate a JWT token here and return it in the response
        return {"message": "Login successful"}
