'''Handling Comment Section'''
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select

from social_media.auth.models import User, Comment, Post, CommentResponse
from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.database import async_session_maker
from social_media.helpers.auth_user import get_authenticated_user

from .schemas import CommentCreate, CommentResponseCreate

router = APIRouter(prefix="/comment", tags=["Comment"])


@router.post("/comments", dependencies=[Depends(JwtBearer())])
async def create_comment(post_id: int, comment: CommentCreate, token: str = Depends(JwtBearer())):
    '''Creating a Comment (POST)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

        post = await session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Create the comment
        new_comment = Comment(text=comment.text, user_id=user_obj.id, post_id=post_id)

        # Add the comment to the session and commit the changes
        session.add(new_comment)
        await session.commit()

    return {"message": "Comment created successfully"}


@router.post("/comments/{comment_id}/respond", dependencies=[Depends(JwtBearer())])
async def respond_to_comment(comment_id: int, response: CommentResponseCreate, token: str = Depends(JwtBearer())):
    '''Responding to a Comment (POST)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:
        # Check if the comment exists
        comment = await session.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        # Create the comment response
        new_response = CommentResponse(text=response.text, user_id=user_obj.id, comment_id=comment_id)

        # Add the response to the session and commit the changes
        session.add(new_response)
        await session.commit()

        return {"message": "Comment response created successfully"}


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
            select(Comment, User.username, User.name,
                   User.surname).join(User, Comment.user_id == User.id).where(Comment.post_id == post_id)
        )
        # Retrieve the responses for each comment
        post_comments = []
        for comment, username, name, surname in comments:
            responses = await session.execute(
                select(CommentResponse, User.username, User.name,
                       User.surname).join(User, CommentResponse.user_id == User.id).where(
                           CommentResponse.comment_id == comment.id
                       )
            )
            comment_responses = [{
                "id": response.id,
                "text": response.text,
                "created_response": response.created_at.strftime("%Y-%m-%d %H:%M") if response.created_at else None,
                "user_id": response.user_id,
                "user_username": username,
                "user_name": name,
                "user_surname": surname,
            } for response, username, name, surname in responses]
            created_comment = comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else None
            comment_data = {
                "id": comment.id,
                "text": comment.text,
                "created_comment": created_comment,
                "user_id": comment.user_id,
                "user_username": username,
                "user_name": name,
                "user_surname": surname,
                "responses": comment_responses
            }
            post_comments.append(comment_data)

    return post_comments
