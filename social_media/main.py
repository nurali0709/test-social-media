from fastapi import FastAPI

from .auth.router import router as auth_router
from .post.router import router as post_router

app = FastAPI()

app.include_router(auth_router)

app.include_router(post_router)
