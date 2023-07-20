'''Initializing FastAPI'''
from fastapi import FastAPI

from .auth.router import router as auth_router
from .post.router import router as post_router
from .comment.router import router as comment_router
from .subscription.router import router as subscription_router
from .tasks.router import router as celery_router

app = FastAPI()

app.include_router(auth_router)

app.include_router(post_router)

app.include_router(comment_router)

app.include_router(subscription_router)

app.include_router(celery_router)
