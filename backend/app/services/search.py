from elasticsearch import AsyncElasticsearch

from app.core.elasticsearch import INDEX_NAME
from app.schemas.text import SearchHit, SearchResponse


async def search_texts(
    es: AsyncElasticsearch,
    query: str,
    page: int = 1,
    size: int = 20,
    dynasty: str | None = None,
    category: str | None = None,
) -> SearchResponse:
    """Search Buddhist texts in Elasticsearch."""
    must = []
    filter_clauses = []

    if query:
        must.append(
            {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title_zh^3",
                        "title_sa^2",
                        "title_bo",
                        "title_pi",
                        "translator^2",
                        "cbeta_id^4",
                        "taisho_id^4",
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        )
    else:
        must.append({"match_all": {}})

    if dynasty:
        filter_clauses.append({"term": {"dynasty": dynasty}})
    if category:
        filter_clauses.append({"term": {"category": category}})

    body = {
        "query": {
            "bool": {
                "must": must,
                "filter": filter_clauses,
            }
        },
        "highlight": {
            "fields": {
                "title_zh": {},
                "translator": {},
            },
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
        },
        "from": (page - 1) * size,
        "size": size,
    }

    result = await es.search(index=INDEX_NAME, body=body)

    hits = result["hits"]
    total = hits["total"]["value"]

    results = []
    for hit in hits["hits"]:
        src = hit["_source"]
        results.append(
            SearchHit(
                id=src["id"],
                taisho_id=src.get("taisho_id"),
                cbeta_id=src["cbeta_id"],
                title_zh=src["title_zh"],
                translator=src.get("translator"),
                dynasty=src.get("dynasty"),
                category=src.get("category"),
                cbeta_url=src.get("cbeta_url"),
                score=hit["_score"],
                highlight=hit.get("highlight"),
            )
        )

    return SearchResponse(total=total, page=page, size=size, results=results)


async def get_aggregations(es: AsyncElasticsearch) -> dict:
    """Get filter aggregations (dynasties, categories)."""
    body = {
        "size": 0,
        "aggs": {
            "dynasties": {"terms": {"field": "dynasty", "size": 50}},
            "categories": {"terms": {"field": "category", "size": 50}},
        },
    }
    result = await es.search(index=INDEX_NAME, body=body)
    aggs = result["aggregations"]
    return {
        "dynasties": [b["key"] for b in aggs["dynasties"]["buckets"]],
        "categories": [b["key"] for b in aggs["categories"]["buckets"]],
    }
