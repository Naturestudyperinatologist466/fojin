"""Hybrid RAG retrieval: pgvector similarity + Dify dataset search in parallel."""

import asyncio
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ChatSource
from app.services.dify_retrieval import dify_dataset_search
from app.services.embedding import generate_embedding, similarity_search

logger = logging.getLogger(__name__)


def _format_source_label(result: dict) -> str:
    if result.get("title_zh"):
        return f"《{result['title_zh']}》第{result['juan_num']}卷"
    return f"文本#{result['text_id']} 第{result['juan_num']}卷"


async def retrieve_rag_context(
    db: AsyncSession,
    query: str,
    *,
    pgvector_limit: int = 5,
    dify_top_k: int = 3,
) -> tuple[list[ChatSource], str]:
    """Run pgvector + Dify retrieval in parallel and return (sources, context_text).

    Gracefully degrades: returns empty results on any retrieval failure.
    """
    sources: list[ChatSource] = []
    context_text = ""
    t0 = time.monotonic()

    try:
        dify_task = asyncio.ensure_future(dify_dataset_search(query, top_k=dify_top_k))
        query_embedding = await generate_embedding(query)
        t1 = time.monotonic()
        logger.debug("TIMING: Embedding took %.2fs", t1 - t0)

        search_results = await similarity_search(db, query_embedding, limit=pgvector_limit)
        logger.debug("TIMING: pgvector search took %.2fs", time.monotonic() - t1)

        sources = [ChatSource(**r) for r in search_results]
        context_parts = [f"[出处: {_format_source_label(r)}]\n{r['chunk_text']}" for r in search_results]

        try:
            dify_results = await dify_task
            for dr in dify_results:
                sources.append(ChatSource(
                    text_id=0, juan_num=0,
                    chunk_text=dr["chunk_text"], score=dr["score"],
                    title_zh="", source_type="dify",
                ))
                context_parts.append(f"[出处: 佛典知识库]\n{dr['chunk_text']}")
        except Exception:
            logger.warning("Dify retrieval failed, using pgvector results only")

        context_text = "\n\n".join(context_parts)
    except Exception:
        logger.exception("Embedding/search failed, proceeding without RAG context")

    logger.debug("TIMING: Total RAG retrieval took %.2fs", time.monotonic() - t0)
    return sources, context_text
