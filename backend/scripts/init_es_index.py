"""Initialize Elasticsearch index for Buddhist texts."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import AsyncElasticsearch
from app.config import settings
from app.core.elasticsearch import INDEX_NAME, INDEX_SETTINGS


async def main():
    es = AsyncElasticsearch(settings.es_host)
    try:
        if await es.indices.exists(index=INDEX_NAME):
            print(f"Index '{INDEX_NAME}' already exists. Deleting...")
            await es.indices.delete(index=INDEX_NAME)

        await es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)
        print(f"Index '{INDEX_NAME}' created successfully.")
    finally:
        await es.close()


if __name__ == "__main__":
    asyncio.run(main())
