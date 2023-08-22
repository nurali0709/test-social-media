from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from social_media.auth.models import Post
from social_media.helpers.random_recommends import get_random_recommendations


async def get_similarity_matrix(session: AsyncSession):
    '''Calculates similarity matrix between posts based on keywords'''

    posts = await session.execute(select(Post))
    all_posts = posts.scalars().all()

    # Extract keywords from posts
    post_keywords = [post.description for post in all_posts]  # Modify based on your data

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(post_keywords)

    # Calculate cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    return cosine_sim


async def get_similar_posts(session: AsyncSession, post_id: int, similarity_matrix):
    '''Get similar posts based on similarity matrix'''

    post_index = post_id - 1

    if 0 <= post_index < len(similarity_matrix):
        similar_scores = list(enumerate(similarity_matrix[post_index]))

        # Sort posts by similarity score in descending order
        sorted_similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)

        # Exclude the current post and get top recommendations
        top_recommendations = []
        for post_index, _ in sorted_similar_scores[1:4]:  # Get top 3 recommendations
            post = await session.get(Post, post_index + 1)  # Adjust for zero-based indexing
            if post:
                top_recommendations.append(post)

        return top_recommendations
    else:
        random_recommendations = await get_random_recommendations(session, post_id)
        return random_recommendations
