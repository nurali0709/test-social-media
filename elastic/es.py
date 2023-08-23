# from elasticsearch import Elasticsearch
# from unidecode import unidecode

# es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# # Creation of post
# post_data = {
#         "id": new_post.id,
#         "title": new_post.title,
#         "description": new_post.description,
#         "likes": new_post.likes,
#         "dislikes": new_post.dislikes,
#         "author": new_post.author_id
#     }

# es.index(index='posts', id=new_post.id, body=post_data)

# # Searching post
# search_results = es.search(index='posts', body={
#             'query': {
#                 'bool': {
#                     'should': [
#                         {'term': {'title': q}},
#                         {'term': {'description': q}}
#                     ]
#                 }
#             }
#         })

#         # Extract the required data for posts
# formatted_posts = []
# for hit in search_results['hits']['hits']:
#             post_data = hit['_source']
#             formatted_post = await format_post_data(post_data, session)
#             formatted_posts.append(formatted_post)

# return formatted_posts
