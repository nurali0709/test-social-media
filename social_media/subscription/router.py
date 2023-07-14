'''Handling Subscription section'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from social_media.auth.jwt.jwt_bearer import JwtBearer
from social_media.auth.jwt.jwt_handler import verify_token
from social_media.auth.models import Subscription, User, Post
from social_media.database import async_session_maker
from social_media.helpers.auth_user import get_authenticated_user

from .schemas import SubscriptionSchema

router = APIRouter(
    prefix="/subscription",
    tags = ["Subscription"]
)

@router.post("/subscriptions", dependencies=[Depends(JwtBearer())])
async def create_subscription(subscription: SubscriptionSchema, token: str = Depends(JwtBearer())):
    '''Subscribing to users'''
    # Retrieve the authenticated user
    subscriber_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:
        # Check if the subscription already exists
        existing_subscription = await session.execute(
            select(Subscription)
            .where(Subscription.subscriber_id == subscriber_obj.id)
            .where(Subscription.subscribed_to_id == subscription.subscribed_to_id)
        )
        if existing_subscription.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Subscription already exists")

        # Check if the subscriber is trying to subscribe themselves
        if subscriber_obj.id == subscription.subscribed_to_id:
            raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

        # Create a new subscription
        new_subscription = Subscription(
            subscriber_id=subscriber_obj.id,
            subscribed_to_id=subscription.subscribed_to_id
        )

        # Save the subscription to the database
        session.add(new_subscription)
        await session.commit()

    return {"message": "Subscription created successfully"}


@router.get("/subscribed_posts", dependencies=[Depends(JwtBearer())])
async def get_subscribed_posts(token: str = Depends(JwtBearer())):
    '''Retrieving all subscribed users posts'''
    # Retrieve the authenticated user
    user_obj = await get_authenticated_user(token)

    async with async_session_maker() as session:

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
async def get_user_subscriptions(user_id: int):
    '''Retrieve the subscriptions for the given user as the subscriber'''
    async with async_session_maker() as session:
        subscriptions = await session.execute(
            select(Subscription, User)
            .join(User, User.id == Subscription.subscribed_to_id)
            .where(Subscription.subscriber_id == user_id)
        )
        user_subscriptions = [{
            "id": subscription.id,
            "subscriber_id": subscription.subscriber_id,
            "subscribed_to_id": subscription.subscribed_to_id,
            "subscribed_to_username": user.username
        } for subscription, user in subscriptions]

    return user_subscriptions

@router.get("/subscribers/{user_id}", dependencies=[Depends(JwtBearer())])
async def get_subscribers(user_id: int):
    '''Retrieve the subscribers of the given user'''
    async with async_session_maker() as session:
        subscriptions = await session.execute(
            select(Subscription, User)
            .join(User, User.id == Subscription.subscriber_id)
            .where(Subscription.subscribed_to_id == user_id)
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
    '''Deleting subscription'''
    # Retrieve the user ID from the JWT token
    username = await verify_token(token)

    async with async_session_maker() as session:
        # Retrieve the subscription with eager loading of the subscriber relationship
        subscription = await session.execute(
            select(Subscription).where(Subscription.id == subscription_id).options(joinedload(Subscription.subscriber))
        )
        existing_subscription = subscription.scalar_one_or_none()

        if not existing_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Retrieve the subscriber's username
        subscriber_username = existing_subscription.subscriber.username

        # Check if the authenticated user is the owner of the subscription
        if subscriber_username != username:
            raise HTTPException(status_code=403, detail="Unauthorized to delete the subscription")

        # Delete the subscription
        await session.delete(existing_subscription)
        await session.commit()

    return {"message": "Subscription deleted successfully"}
