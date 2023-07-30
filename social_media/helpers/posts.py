from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from social_media.auth.models import Post, User, Comment, CommentResponse


async def get_formatted_posts(session, ordering):
    posts = await session.execute(select(Post).join(User).options(joinedload(Post.author)).order_by(ordering))
    all_posts = posts.scalars().all()

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
