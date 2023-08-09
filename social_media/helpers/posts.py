'''Shortening posts response'''
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from social_media.auth.models import Post, User
from social_media.utils.format_post import format_post_data


async def get_formatted_posts(session, ordering):
    '''Helper to shorten posts query'''
    posts = await session.execute(select(Post).join(User).options(joinedload(Post.author)).order_by(ordering))
    all_posts = posts.scalars().all()

    formatted_posts = []
    for post in all_posts:
        # Use the format_post_data function to format the post data
        formatted_post = await format_post_data(post, session)
        formatted_posts.append(formatted_post)

    return formatted_posts
