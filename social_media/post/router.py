'''Handling post endpoint'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, func, desc
from sqlalchemy.orm import joinedload, aliased

from social_media.auth.models import Post, User, Reaction, Comment, CommentResponse
from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.database import async_session_maker
from social_media.helpers.auth_user import get_authenticated_user
from social_media.helpers.recommends import get_random_recommendations
from .schemas import PostSchema

router = APIRouter(prefix="/post", tags=["Post"])


@router.get("/posts")
async def get_posts():
    '''Getting all posts (GET)'''
    async with async_session_maker() as session:
        posts = await session.execute(
            select(Post).join(User).options(joinedload(Post.author)).order_by(desc(Post.created_at))
        )
        all_posts = posts.scalars().all()

    # Extract the required data and include the author's username
    formatted_posts = []
    for post in all_posts:
        # Count the number of comments for the post
        num_comments = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post.id))
        num_comments = num_comments.scalar()

        # Count the number of comment responses for the post
        num_comment_responses = await session.execute(
            select(func.count(CommentResponse.id)
                   ).join(Comment, Comment.id == CommentResponse.comment_id).where(Comment.post_id == post.id)
        )
        num_comment_responses = num_comment_responses.scalar()

        # Calculate the total number of comments and comment responses
        comments = num_comments + num_comment_responses

        author_username = post.author.username if post.author else None
        author_name = post.author.name if post.author else None
        author_surname = post.author.surname if post.author else None
        # Handle the case when created_at is None
        created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
        updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None

        formatted_posts.append({
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "views": post.views,
            "comments": comments,
            "author_id": post.author_id,
            "author_username": author_username,
            "author_name": author_name,
            "author_surname": author_surname,
            "created_at": created_at,
            "updated_at": updated_at,
        })

    return formatted_posts


@router.get("/posts/order_likes")
async def get_posts_ordered_by_likes():
    '''Getting all posts ordered by likes (GET)'''
    async with async_session_maker() as session:
        posts = await session.execute(
            select(Post).join(User).options(joinedload(Post.author)).order_by(desc(Post.likes))
        )
        all_posts = posts.scalars().all()

    # Extract the required data and include the author's username
    formatted_posts = []
    for post in all_posts:
        # Count the number of comments for the post
        num_comments = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post.id))
        num_comments = num_comments.scalar()

        # Count the number of comment responses for the post
        num_comment_responses = await session.execute(
            select(func.count(CommentResponse.id)
                   ).join(Comment, Comment.id == CommentResponse.comment_id).where(Comment.post_id == post.id)
        )
        num_comment_responses = num_comment_responses.scalar()

        # Calculate the total number of comments and comment responses
        comments = num_comments + num_comment_responses

        author_username = post.author.username if post.author else None
        author_name = post.author.name if post.author else None
        author_surname = post.author.surname if post.author else None
        # Handle the case when created_at is None
        created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
        updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None

        formatted_posts.append({
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "views": post.views,
            "comments": comments,
            "author_id": post.author_id,
            "author_username": author_username,
            "author_name": author_name,
            "author_surname": author_surname,
            "created_at": created_at,
            "updated_at": updated_at,
        })

    return formatted_posts


@router.get("/posts/order_views")
async def get_posts_ordered_by_views():
    '''Getting all posts ordered by views (GET)'''
    async with async_session_maker() as session:
        posts = await session.execute(
            select(Post).join(User).options(joinedload(Post.author)).order_by(desc(Post.views))
        )
        all_posts = posts.scalars().all()

    # Extract the required data and include the author's username
    formatted_posts = []
    for post in all_posts:
        # Count the number of comments for the post
        num_comments = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post.id))
        num_comments = num_comments.scalar()

        # Count the number of comment responses for the post
        num_comment_responses = await session.execute(
            select(func.count(CommentResponse.id)
                   ).join(Comment, Comment.id == CommentResponse.comment_id).where(Comment.post_id == post.id)
        )
        num_comment_responses = num_comment_responses.scalar()

        # Calculate the total number of comments and comment responses
        comments = num_comments + num_comment_responses

        author_username = post.author.username if post.author else None
        author_name = post.author.name if post.author else None
        author_surname = post.author.surname if post.author else None
        # Handle the case when created_at is None
        created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
        updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None

        formatted_posts.append({
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "views": post.views,
            "comments": comments,
            "author_id": post.author_id,
            "author_username": author_username,
            "author_name": author_name,
            "author_surname": author_surname,
            "created_at": created_at,
            "updated_at": updated_at,
        })

    return formatted_posts


@router.post("/create_post")
async def create_post(post: PostSchema, token: str = Depends(JwtBearer())):
    '''Creating Post (POST)'''

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

    # Create the post
    new_post = Post(title=post.title, description=post.description, likes=0, dislikes=0, author_id=user_obj.id)

    # Add the post to the session and commit the changes
    async with async_session_maker() as session:
        session.add(new_post)
        await session.commit()

    return {"message": "Post created successfully"}


@router.get("/my_posts", dependencies=[Depends(JwtBearer())])
async def get_user_posts(token: str = Depends(JwtBearer())):
    '''Getting only users post (GET)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

        # Retrieve the user's own posts
        posts = await session.execute(select(Post).where(Post.author_id == user_obj.id))
        user_posts = posts.scalars().all()

    return user_posts


@router.put("/posts/{post_id}", dependencies=[Depends(JwtBearer())])
async def update_post(post_id: int, updated_post: PostSchema, token: str = Depends(JwtBearer())):
    '''Updating Post (PUT)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

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


@router.delete("/posts/{post_id}", dependencies=[Depends(JwtBearer())])
async def delete_post(post_id: int, token: str = Depends(JwtBearer())):
    '''Deleting Post (DELETE)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

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


@router.post("/posts/{post_id}/reaction", dependencies=[Depends(JwtBearer())])
async def react_to_post(post_id: int, reaction: str, token: str = Depends(JwtBearer())):
    '''Reaction to post: like or dislike'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

        # Retrieve the post from the database
        post = await session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Check if the user has already reacted to the post
        reaction_obj = await session.execute(
            select(Reaction).where(Reaction.post_id == post.id, Reaction.user_id == user_obj.id)
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


@router.get("/liked_posts", dependencies=[Depends(JwtBearer())])
async def get_liked_posts(token: str = Depends(JwtBearer())):
    '''Getting all posts liked by the user (GET)'''

    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:
        # Retrieve the posts liked by the user
        liked_posts = await session.execute(
            select(Post).join(Reaction).join(User, User.id == Post.author_id
                                             ).where(Reaction.user_id == user_obj.id,
                                                     Reaction.reaction == "like").options(joinedload(Post.author))
        )
        user_liked_posts = liked_posts.scalars().all()

        # Extract the required data and include the author's username
        formatted_posts = []
        for post in user_liked_posts:
            author_username = post.author.username if post.author else None

            created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
            updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None

            formatted_posts.append({
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "likes": post.likes,
                "dislikes": post.dislikes,
                "views": post.views,
                "author_id": post.author_id,
                "author_username": author_username,
                "created_at": created_at,
                "updated_at": updated_at,
            })

        return formatted_posts


@router.get("/search")
async def search(q: str):
    '''Search posts by title or username (GET)'''

    async with async_session_maker() as session:
        user_alias = aliased(User)
        unique_posts = set()

        # Search for posts with the keyword in their title
        posts_by_title = await session.execute(
            select(Post).join(user_alias, user_alias.id == Post.author_id).where(Post.title.ilike(f"%{q}%")
                                                                                 ).options(joinedload(Post.author))
        )

        # Search for posts with the keyword in the User's name, surname, or username
        posts_by_user = await session.execute(
            select(Post).outerjoin(user_alias, user_alias.id == Post.author_id).where(
                or_(
                    user_alias.name.ilike(f"%{q}%"), user_alias.surname.ilike(f"%{q}%"),
                    user_alias.username.ilike(f"%{q}%")
                )
            ).options(joinedload(Post.author))
        )

        # Extract the required data for posts
        formatted_posts = []
        for post in posts_by_title.scalars().all() + posts_by_user.scalars().all():
            if post.id not in unique_posts:
                unique_posts.add(post.id)

                author_username = post.author.username if post.author else None
                author_name = post.author.name if post.author else None
                author_surname = post.author.surname if post.author else None

                created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
                updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None

                formatted_posts.append({
                    "id": post.id,
                    "title": post.title,
                    "description": post.description,
                    "likes": post.likes,
                    "dislikes": post.dislikes,
                    "views": post.views,
                    "author_id": post.author_id,
                    "author_username": author_username,
                    "author_name": author_name,
                    "author_surname": author_surname,
                    "created_at": created_at,
                    "updated_at": updated_at,
                })

        return formatted_posts


@router.get("/posts/{post_id}/view")
async def view_post(post_id: int):
    '''Increment the view count of a post (GET)'''

    async with async_session_maker() as session:

        post_with_author = (
            await session.execute(select(Post, User).join(User, User.id == Post.author_id).where(Post.id == post_id))
        ).first()

        if not post_with_author:
            raise HTTPException(status_code=404, detail="Post not found")

        post, author = post_with_author

        # Increment the view count
        post.views += 1
        await session.commit()

        # Count the number of comments for the post
        num_comments = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id))
        num_comments = num_comments.scalar()

        # Count the number of comment responses for the post
        num_comment_responses = await session.execute(
            select(func.count(CommentResponse.id)
                   ).join(Comment, Comment.id == CommentResponse.comment_id).where(Comment.post_id == post_id)
        )
        num_comment_responses = num_comment_responses.scalar()

        # Calculate the total number of comments and comment responses
        total_num_comments = num_comments + num_comment_responses

        # Return the updated view count and the three random recommended posts
        recommendations = await get_random_recommendations(session, post_id)
        created_at = post.created_at.strftime("%Y-%m-%d") if post.created_at else None
        updated_at = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "likes": post.likes,
                "dislikes": post.dislikes,
                "views": post.views,
                "total_num_comments": total_num_comments,
                "author": {
                    "id": author.id,
                    "username": author.username,
                    "name": author.name,
                    "surname": author.surname,
                },
                "created_at": created_at,
                "updated_at": updated_at,
            },
            "recommendations": recommendations
        }
