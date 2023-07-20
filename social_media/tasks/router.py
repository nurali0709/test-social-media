'''Handling Celery worker task'''
import bcrypt

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from social_media.auth.models import User
from social_media.database import async_session_maker
from social_media.helpers.verification import generate_verification_code
from .tasks import send_verification_code

router = APIRouter(
    prefix="/celery",
    tags = ["Celery"]
)

@router.post("/forgot_password")
async def forgot_password(email: str):
    '''Send verification code to the provided email for password reset'''

    async with async_session_maker() as session:
        db_user = await session.execute(select(User).where(User.email == email))
        user_obj = db_user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=404, detail="Email not found")

        # Generate and save the verification code (you can use your own implementation here)
        verification_code = generate_verification_code()
        user_obj.verification_code = verification_code
        await session.commit()

        # Send the verification code to the user's email using Celery
        send_verification_code.delay(user_obj.email, verification_code)

        return {"message": "Verification code sent to email"}

@router.post("/reset_password")
async def reset_password(email: str, verification_code: str, new_password: str):
    '''Reset user's password using the verification code'''

    async with async_session_maker() as session:
        db_user = await session.execute(select(User).where(User.email == email))
        user_obj = db_user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=404, detail="Email not found")

        if not user_obj.verification_code:
            raise HTTPException(status_code=400, detail="Verification code not generated or already used")

        if user_obj.verification_code != verification_code:
            raise HTTPException(status_code=400, detail="Invalid verification code")

        # Reset the password and clear the verification code
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        user_obj.password = hashed_password.decode("utf-8")
        user_obj.verification_code = None
        await session.commit()

        return {"message": "Password reset successful"}
