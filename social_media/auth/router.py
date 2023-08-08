'''Handling Authentication'''
import bcrypt

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from social_media.database import async_session_maker
from social_media.helpers.auth_user import get_authenticated_user
from .models import User
from .schemas import UserSignup, UserLogin, UserUpdate

from .jwt.jwt_handler import jwt_sign, verify_token
from .jwt.jwt_bearer import JwtBearer

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
async def signup(user: UserSignup, response: Response):
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
        db_user = User(
            username=user.username,
            password=hashed_password.decode("utf-8"),
            email=user.email,
            name=user.name,
            surname=user.surname
        )

        session.add(db_user)
        await session.commit()

        # Generate a JWT token
        token = jwt_sign(user.username)

        return {"jwt": token}


@router.post("/login")
async def login(user: UserLogin, response: Response):
    '''Login user with JWT'''
    async with async_session_maker() as session:
        db_user = await session.execute(select(User).where(User.username == user.username))
        user_obj = db_user.scalar_one_or_none()

        if not user_obj or not bcrypt.checkpw(user.password.encode("utf-8"), user_obj.password.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Generate a JWT token
        token = jwt_sign(user.username)

        return {
            "user": {
                "id": user_obj.id,
                "username": user_obj.username,
                "name": user_obj.name,
                "surname": user_obj.surname,
                "email": user_obj.email,
                # Add more user data fields as needed
            },
            "jwt": token
        }


@router.post("/logout")
async def logout(response: Response, token: str = Depends(JwtBearer())):
    '''Logout user and delete token cookie'''

    if not token:
        raise HTTPException(status_code=401, detail="No token found in the cookie")

    try:
        username = await verify_token(token)
    except HTTPException as exc:
        raise exc

    return {"message": "Logout successful"}


@router.put("/users/{user_id}/update")
async def update_user(user_id: int, user_update: UserUpdate, token: str = Depends(JwtBearer())):
    '''Update user data (PUT)'''

    # Retrieve the authenticated user
    authenticated_user = await get_authenticated_user(token)

    # Ensure that the user can only update their own data
    if authenticated_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden - You can only update your own data")

    async with async_session_maker() as session:
        # Retrieve the user from the database
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user data with the new values
        user.username = user_update.username
        user.email = user_update.email
        user.name = user_update.name
        user.surname = user_update.surname

        # Commit the changes to the database
        await session.commit()

    return UserUpdate(id=user.id, username=user.username, email=user.email, name=user.name, surname=user.surname)


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
