'''Handling Comment Section'''
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select

from social_media.auth.models import User, Comment, Post
from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.database import async_session_maker

from .schemas import CommentCreate

router = APIRouter(
    prefix="/comment",
    tags = ["Comment"]
)

@router.post("/comments", dependencies=[Depends(JwtBearer())])
async def create_comment(post_id: int, comment: CommentCreate, token: str = Depends(JwtBearer())):
    '''Creating a Comment (POST)'''

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Create the comment
        new_comment = Comment(text=comment.text, user_id=user_obj.id, post_id=post_id)

        # Add the comment to the session and commit the changes
        session.add(new_comment)
        await session.commit()

    return {"message": "Comment created successfully"}

@router.get("/comments/{post_id}")
async def get_post_comments(post_id: int):
    '''Getting comments for a post (GET)'''

    async with async_session_maker() as session:
        # Retrieve the post from the database
        post = await session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Retrieve the comments for the post, including the associated user's username
        comments = await session.execute(
            select(Comment, User.username)
            .join(User, Comment.user_id == User.id)
            .where(Comment.post_id == post_id)
        )
        post_comments = [
            {"id": comment.id, "text": comment.text, "user_id": comment.user_id, "user_username": username}
            for comment, username in comments
        ]

    return post_comments
