from fastapi import APIRouter, Query

from app.core.elasticsearch import get_es
from app.schemas.text import SearchResponse
from app.services.search import get_aggregations, search_texts

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query("", description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    dynasty: str | None = Query(None, description="朝代筛选"),
    category: str | None = Query(None, description="分类筛选"),
):
    """搜索佛教典籍。支持经名、编号、译者等多字段搜索。"""
    es = get_es()
    return await search_texts(es, q, page, size, dynasty, category)


@router.get("/filters")
async def filters():
    """获取可用的筛选选项（朝代、分类）。"""
    es = get_es()
    return await get_aggregations(es)
