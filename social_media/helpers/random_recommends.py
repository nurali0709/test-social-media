'''Recommendation maker helper'''
from typing import List
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from social_media.auth.models import Post, User


async def get_random_recommendations(session: AsyncSession, post_id: int) -> List[Post]:
    '''Handling generating recommendation posts'''
    result = (
        await session.execute(
            select(Post, User).join(User,
                                    User.id == Post.author_id).where(Post.id != post_id)  # Exclude the current post
        )
    )

    recommended_posts = []
    for post, author in result:
        post_data = {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "views": post.views,
            "created_at": post.created_at.strftime("%Y-%m-%d") if post.created_at else None,
            "updated_at": post.updated_at.strftime("%Y-%m-%d") if post.updated_at else None,
            "author": {
                "id": author.id,
                "username": author.username,
                "name": author.name,
                "surname": author.surname,
            }
        }
        recommended_posts.append(post_data)

    # Choose three random posts from the recommendations
    num_recommendations = min(3, len(recommended_posts))
    random_recommendations = random.sample(recommended_posts, num_recommendations)

    return random_recommendations
