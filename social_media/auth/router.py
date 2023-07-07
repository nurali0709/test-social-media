from fastapi import APIRouter, HTTPException
from .schemas import UserLogin, UserSignup

router = APIRouter(
    prefix="/auth",
    tags = ["Auth"]
)

database = {}

@router.post("/signup")
async def signup(user: UserSignup):
    if user.username in database:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Save the user in the database (you may want to hash the password for security)
    database[user.username] = {"username": user.username, "password": user.password}
    return {"message": "Signup successful"}

@router.post("/login")
async def login(user: UserLogin):
    if user.username not in database or database[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # You can generate a JWT token here and return it in the response
    return {"message": "Login successful"}
