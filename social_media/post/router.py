'''Handling post endpoint'''
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import aliased, joinedload

from social_media.auth.models import Comment, CommentResponse, Post, Reaction, User
from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.database import async_session_maker
from social_media.elastic.search import Search
from social_media.helpers.auth_user import get_authenticated_user
from social_media.ai.recommendations import get_similar_posts, get_similarity_matrix
from social_media.helpers.posts import get_formatted_posts
from social_media.utils.format_post import format_post_data
from .schemas import PostSchema

router = APIRouter(prefix="/post", tags=["Post"])


class IndexResource:

    def __init__(self):
        self.search = Search()


@router.get("/posts")
async def get_posts():
    '''Getting all posts (GET)'''
    async with async_session_maker() as session:
        return await get_formatted_posts(session, desc(Post.created_at))


@router.get("/posts/order_likes")
async def get_posts_ordered_by_likes():
    '''Getting all posts ordered by likes (GET)'''
    async with async_session_maker() as session:
        return await get_formatted_posts(session, desc(Post.likes))


@router.get("/posts/order_views")
async def get_posts_ordered_by_views():
    '''Getting all posts ordered by views (GET)'''
    async with async_session_maker() as session:
        return await get_formatted_posts(session, desc(Post.views))


@router.post("/create_post")
async def create_post(
    title: str,
    description: str,
    image: UploadFile = File(None),
    index_resource: IndexResource = Depends(IndexResource),
    token: str = Depends(JwtBearer()),
):
    '''Creating Post (POST)'''

    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

    new_post = Post(title=title, description=description, likes=0, dislikes=0, author_id=user_obj.id)

    if image:
        image_data = await image.read()
        image_filename = f"post_{new_post.title}_image.jpg"
        image_path = os.path.join("static", image_filename)

        with open(image_path, "wb") as f:
            f.write(image_data)

        new_post.image = str("static/" + image_filename)

    # Add the post to the session and commit the changes
    async with async_session_maker() as session:
        session.add(new_post)
        await session.commit()

    post_document = {"title": new_post.title, "description": new_post.description}

    doc = index_resource.search.create_document(index_name='posts', document=post_document, id=new_post.id)

    return {"message": "Post created successfully", "data": doc}


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
async def update_post(
    post_id: int,
    updated_post: PostSchema,
    token: str = Depends(JwtBearer()),
    index_resource: IndexResource = Depends(IndexResource)
):
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

        post_document = {"title": existing_post.title, "description": existing_post.description}

        index_resource.search.update_document(index_name='posts', document=post_document, id=existing_post.id)

    return {"message": "Post updated successfully"}


@router.delete("/posts/{post_id}", dependencies=[Depends(JwtBearer())])
async def delete_post(
    post_id: int, token: str = Depends(JwtBearer()), index_resource: IndexResource = Depends(IndexResource)
):
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

        index_resource.search.delete_document(index_name='posts', id=post.id)

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

                # Use the format_post_data function to format the post data
                formatted_post = await format_post_data(post, session)
                formatted_posts.append(formatted_post)

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

        similarity_matrix = await get_similarity_matrix(session)
        recommendations = await get_similar_posts(session, post_id, similarity_matrix)

        # recommendations = await get_random_recommendations(session, post_id)
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


@router.get("/users/{user_id}/posts")
async def get_any_user_posts(user_id: int):
    '''Getting all posts by a user (GET)'''

    async with async_session_maker() as session:

        # Retrieve the user from the database
        user = await session.execute(select(User).where(User.id == user_id))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve the user's posts
        posts = await session.execute(select(Post).where(Post.author_id == user_obj.id))
        user_posts = posts.scalars().all()

        return user_posts


@router.get("/users/{user_id}/liked_posts")
async def get_user_liked_posts(user_id: int):
    '''Getting all posts liked by a user (GET)'''

    async with async_session_maker() as session:

        # Retrieve the user from the database
        user = await session.execute(select(User).where(User.id == user_id))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

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


@router.get("/elasticsearch")
async def elastic_search_posts(q: str, index_resource: IndexResource = Depends(IndexResource)):
    '''Search posts by title or description (GET)'''

    # Define the Elasticsearch search query
    search_query = {"query": {"multi_match": {"query": q, "fields": ["title", "description"]}}}

    # Search posts using Elasticsearch
    try:
        search_results = index_resource.search.get_data(index_name='posts', search_query=search_query, size=10)
    except Exception:
        raise HTTPException(status_code=500, detail="Error while querying Elasticsearch")

    formatted_posts = []
    for hit in search_results['hits']['hits']:
        formatted_posts.append(hit['_source'])

    return formatted_posts
