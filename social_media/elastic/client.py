from opensearchpy import OpenSearch, RequestsHttpConnection


class ElasticCacheClient:

    @staticmethod
    def get_client():
        client = OpenSearch(hosts=[{'host': 'localhost', 'port': 9200}], connection_class=RequestsHttpConnection)
        print(client.info())
        return client
