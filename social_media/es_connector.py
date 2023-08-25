from elasticsearch import Elasticsearch


class EsConnector:

    def __init__(self) -> None:
        self.es_client = None
        self.connect()

    def connect(self):
        host = "localhost"
        port = "9200"
        es = Elasticsearch({'host': host, "port": port})
        self.es_client = es

    def insert_document(self, index_name, document_type, document_id, document, refresh=False):
        try:
            return self.es_client.index(index=index_name, id=document_id, body=document, refresh='wait_for')
        except Exception as e:
            print(e)

    def get_data(self, index_name, search_query, size=10):
        try:
            result = self.es_client.search(index=index_name, body=search_query, size=size)
            return result
        except Exception as e:
            print(e)
