from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.text import TextResponse
from app.services.text import get_text_by_id, get_text_count

router = APIRouter(tags=["texts"])


@router.get("/texts/{text_id}", response_model=TextResponse)
async def get_text(text_id: int, db: AsyncSession = Depends(get_db)):
    """获取经典详情。"""
    text = await get_text_by_id(db, text_id)
    if not text:
        raise HTTPException(status_code=404, detail="经典未找到")
    return text


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    """获取平台统计数据。"""
    count = await get_text_count(db)
    return {"total_texts": count}
