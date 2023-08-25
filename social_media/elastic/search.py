from typing import Any
from .client import ElasticCacheClient


class Search:

    def __init__(self):
        self.client = ElasticCacheClient.get_client()

    def create_document(self, index_name, document, id) -> Any:
        return self.client.index(index=index_name, body=document, id=id, refresh=True)

    def delete_document(self, index_name, id) -> Any:
        return self.client.delete(index=index_name, id=id)

    def update_document(self, index_name, document, id) -> Any:
        return self.client.update(index=index_name, id=id, body={"doc": document})

    def get_data(self, index_name, search_query, size=10):
        try:
            result = self.client.search(index=index_name, body=search_query, size=size)
            return result
        except Exception as e:
            print("Error:", e)
            raise e
