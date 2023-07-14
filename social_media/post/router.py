'''Handling post endpoint'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from social_media.auth.models import Post, User, Reaction, Comment, Subscription
from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.database import async_session_maker

from .schemas import PostSchema, SubscriptionSchema

router = APIRouter(
    prefix="/post",
    tags = ["Post"]
)

@router.get("/posts")
async def get_posts():
    '''Getting all posts (GET)'''
    async with async_session_maker() as session:
        posts = await session.execute(select(Post))
        all_posts = posts.scalars().all()
    return all_posts

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

@router.put("/posts/{post_id}", dependencies=[Depends(JwtBearer())])
async def update_post(post_id: int, updated_post: PostSchema, token: str = Depends(JwtBearer())):
    '''Updating Post (PUT)'''

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

@router.delete("/posts/{post_id}", dependencies=[Depends(JwtBearer())])
async def delete_post(post_id: int, token: str = Depends(JwtBearer())):
    '''Deleting Post (DELETE)'''

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

@router.post("/posts/{post_id}/reaction", dependencies=[Depends(JwtBearer())])
async def react_to_post(post_id: int, reaction: str, token: str = Depends(JwtBearer())):
    '''Reaction to post: like or dislike'''

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

@router.post("/subscriptions", dependencies=[Depends(JwtBearer())])
async def create_subscription(user_id: int, subscription: SubscriptionSchema, token: str = Depends(JwtBearer())):
    # Validate subscriber_id and subscribed_to_id
    if user_id == subscription.subscribed_to_id:
        raise HTTPException(status_code=400, detail="User cannot subscribe to themselves")

    # Create a new subscription
    new_subscription = Subscription(
        subscriber_id=user_id,
        subscribed_to_id=subscription.subscribed_to_id
    )

    # Save the subscription to the database
    async with async_session_maker() as session:
        session.add(new_subscription)
        await session.commit()

    return {"message": "Subscription created successfully"}

@router.get("/subscribed_posts", dependencies=[Depends(JwtBearer())])
async def get_subscribed_posts(token: str = Depends(JwtBearer())):
    # Get the user ID from the JWT token
    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the user from the database based on the username
        user = await session.execute(select(User).where(User.username == username))
        user_obj = user.scalar_one_or_none()

        if not user_obj:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve the IDs of the users that the current user is subscribed to
        subscriptions = await session.execute(
            select(Subscription.subscribed_to_id).where(Subscription.subscriber_id == user_obj.id)
        )
        subscribed_user_ids = [sub[0] for sub in subscriptions]

        # Retrieve the posts from the subscribed users
        posts = await session.execute(
            select(Post).where(Post.author_id.in_(subscribed_user_ids))
        )
        subscribed_posts = posts.scalars().all()

    return subscribed_posts


@router.get("/subscriptions/{user_id}", dependencies=[Depends(JwtBearer())])
async def get_user_subscriptions(user_id: int, token: str = Depends(JwtBearer())):
    # Retrieve the subscriptions for the given user as the subscriber
    async with async_session_maker() as session:
        subscriptions = await session.execute(
            select(Subscription, User).join(User, User.id == Subscription.subscribed_to_id).where(Subscription.subscriber_id == user_id)
        )
        user_subscriptions = [{
            "id": subscription.id,
            "subscriber_id": subscription.subscriber_id,
            "subscribed_to_id": subscription.subscribed_to_id,
            "subscribed_to_username": user.username
        } for subscription, user in subscriptions]

    return user_subscriptions

@router.get("/subscribers/{user_id}", dependencies=[Depends(JwtBearer())])
async def get_subscribers(user_id: int, token: str = Depends(JwtBearer())):
    # Retrieve the subscribers of the given user
    async with async_session_maker() as session:
        subscriptions = await session.execute(
            select(Subscription, User).join(User, User.id == Subscription.subscriber_id).where(Subscription.subscribed_to_id == user_id)
        )
        subscribers = [{
            "id": subscription.id,
            "subscriber_id": subscription.subscriber_id,
            "subscriber_username": user.username,
            "subscribed_to_id": subscription.subscribed_to_id
        } for subscription, user in subscriptions]

    return subscribers

@router.delete("/subscriptions/{subscription_id}", dependencies=[Depends(JwtBearer())])
async def delete_subscription(subscription_id: int, token: str = Depends(JwtBearer())):
    # Retrieve the subscription
    async with async_session_maker() as session:
        subscription = await session.get(Subscription, subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Delete the subscription
        await session.delete(subscription)
        await session.commit()

    return {"message": "Subscription deleted successfully"}
