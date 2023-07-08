import bcrypt
import uuid
import jwt

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from .models import User, Post, Reaction
from .schemas import UserSignup, UserLogin, PostCreate
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

@router.post("/create_post")
async def create_post(post: PostCreate, token: str = Depends(jwt_bearer())):
    # Token verification has already been handled by the JWTBearer dependency
    # You can extract the username from the token payload and proceed with creating the post

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

    # Create the post with the provided data and assign the user's id as the author_id
    new_post = Post(title=post.title, description=post.description, likes=0, dislikes=0, author_id=user_obj.id)

    # Add the post to the session and commit the changes
    async with async_session_maker() as session:
        session.add(new_post)
        await session.commit()

    return {"message": "Post created successfully"}

@router.get("/posts")
async def get_posts():
    async with async_session_maker() as session:
        posts = await session.execute(select(Post))
        all_posts = posts.scalars().all()
    return all_posts

@router.get("/my_posts", dependencies=[Depends(jwt_bearer())])
async def get_user_posts(token: str = Depends(jwt_bearer())):
    # Token verification has already been handled by the jwt_bearer dependency
    # You can extract the username from the token payload and retrieve the user's own posts

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve the user's own posts
        posts = await session.execute(select(Post).where(Post.author_id == user_obj.id))
        user_posts = posts.scalars().all()

    return user_posts

@router.put("/posts/{post_id}", dependencies=[Depends(jwt_bearer())])
async def update_post(post_id: int, updated_post: PostCreate, token: str = Depends(jwt_bearer())):
    # Token verification has already been handled by the jwt_bearer dependency
    # You can extract the username from the token payload and update the post

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve the post from the database
        post = await session.execute(select(Post).where(Post.id == post_id).where(Post.author_id == user_obj.id))
        existing_post = post.scalar_one_or_none()

        if not existing_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Update the post with the provided data
        existing_post.title = updated_post.title
        existing_post.description = updated_post.description

        await session.commit()

    return {"message": "Post updated successfully"}

@router.delete("/posts/{post_id}", dependencies=[Depends(jwt_bearer())])
async def delete_post(post_id: int, token: str = Depends(jwt_bearer())):

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve the post from the database
        post = await session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Check if the authenticated user is the author of the post
        if post.author_id != user_obj.id:
            raise HTTPException(status_code=403, detail="Unauthorized to delete the post")

        # Delete the post
        await session.delete(post)
        await session.commit()
    return {"message": "Post deleted successfully"}

@router.post("/posts/{post_id}/reaction", dependencies=[Depends(jwt_bearer())])
async def react_to_post(post_id: int, reaction: str, token: str = Depends(jwt_bearer())):

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve the post from the database
        post = await session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Check if the user has already reacted to the post
        reaction_obj = await session.execute(
            select(Reaction).where(
                Reaction.post_id == post.id,
                Reaction.user_id == user_obj.id
            )
        )
        existing_reaction = reaction_obj.scalar_one_or_none()

        if existing_reaction:
            # User has already reacted to the post, update the reaction
            if existing_reaction.reaction == reaction:
                raise HTTPException(status_code=400, detail="User has already reacted with the same reaction")

            # Update the reaction and save changes
            existing_reaction.reaction = reaction
            await session.commit()
        else:
            # Check if the user is the author of the post
            if user_obj.id == post.author_id:
                raise HTTPException(status_code=403, detail="User cannot react to their own post")
            
            # User has not reacted to the post, create a new reaction
            new_reaction = Reaction(post_id=post.id, user_id=user_obj.id, reaction=reaction)
            session.add(new_reaction)
            await session.commit()

            # Increment the likes or dislikes count based on the reaction
            if reaction == "like":
                post.likes += 1
            elif reaction == "dislike":
                post.dislikes += 1
            await session.commit()

    return {"message": "Reaction recorded successfully"}
