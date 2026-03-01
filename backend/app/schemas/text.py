from datetime import datetime

from pydantic import BaseModel


class TextBase(BaseModel):
    taisho_id: str | None = None
    cbeta_id: str
    title_zh: str
    title_sa: str | None = None
    title_bo: str | None = None
    title_pi: str | None = None
    translator: str | None = None
    dynasty: str | None = None
    fascicle_count: int | None = None
    category: str | None = None
    subcategory: str | None = None
    cbeta_url: str | None = None


class TextResponse(TextBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchHit(BaseModel):
    id: int
    taisho_id: str | None = None
    cbeta_id: str
    title_zh: str
    translator: str | None = None
    dynasty: str | None = None
    category: str | None = None
    cbeta_url: str | None = None
    score: float | None = None
    highlight: dict[str, list[str]] | None = None


class SearchResponse(BaseModel):
    total: int
    page: int
    size: int
    results: list[SearchHit]
