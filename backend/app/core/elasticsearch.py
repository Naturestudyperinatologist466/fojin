from elasticsearch import AsyncElasticsearch

from app.config import settings

es_client: AsyncElasticsearch | None = None

INDEX_NAME = "buddhist_texts"

INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "analyzer": {
                "cjk_bigram": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["cjk_bigram", "lowercase"],
                },
            }
        }
    },
    "mappings": {
        "properties": {
            "taisho_id": {"type": "keyword"},
            "cbeta_id": {"type": "keyword"},
            "title_zh": {
                "type": "text",
                "analyzer": "cjk_bigram",
                "fields": {"raw": {"type": "keyword"}},
            },
            "title_sa": {"type": "text", "analyzer": "standard"},
            "title_bo": {"type": "text", "analyzer": "standard"},
            "title_pi": {"type": "text", "analyzer": "standard"},
            "translator": {
                "type": "text",
                "analyzer": "cjk_bigram",
                "fields": {"raw": {"type": "keyword"}},
            },
            "dynasty": {"type": "keyword"},
            "category": {"type": "keyword"},
            "subcategory": {"type": "keyword"},
            "fascicle_count": {"type": "integer"},
            "cbeta_url": {"type": "keyword", "index": False},
        }
    },
}


async def init_es() -> AsyncElasticsearch:
    global es_client
    es_client = AsyncElasticsearch(settings.es_host)
    return es_client


async def close_es():
    global es_client
    if es_client:
        await es_client.close()
        es_client = None


def get_es() -> AsyncElasticsearch:
    if es_client is None:
        raise RuntimeError("Elasticsearch client not initialized")
    return es_client
