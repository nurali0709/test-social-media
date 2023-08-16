import humanize
from datetime import datetime, timedelta
from sqlalchemy import select, func
from social_media.auth.models import Comment, CommentResponse


async def format_post_data(post, session):
    num_comments = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post.id))
    num_comments = num_comments.scalar()

    num_comment_responses = await session.execute(
        select(func.count(CommentResponse.id)
               ).join(Comment, Comment.id == CommentResponse.comment_id).where(Comment.post_id == post.id)
    )
    num_comment_responses = num_comment_responses.scalar()

    comments = num_comments + num_comment_responses

    author_username = post.author.username if post.author else None
    author_name = post.author.name if post.author else None
    author_surname = post.author.surname if post.author else None

    created_at = post.created_at
    updated_at = post.updated_at

    if created_at:
        time_difference = datetime.utcnow() - created_at
        created_time_ago = humanize.naturaltime(time_difference)
    else:
        created_time_ago = None

    if updated_at:
        time_difference = datetime.utcnow() - updated_at
        updated_time_ago = humanize.naturaltime(time_difference)
    else:
        updated_time_ago = None

    return {
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
        "created_time_ago": created_time_ago,
        "updated_time_ago": updated_time_ago,
    }
