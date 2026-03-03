from datetime import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    text_id: int
    note: str | None = None


class BookmarkResponse(BaseModel):
    id: int
    text_id: int
    title_zh: str
    cbeta_id: str
    note: str | None = None
    created_at: datetime


class HistoryResponse(BaseModel):
    id: int
    text_id: int
    title_zh: str
    cbeta_id: str
    juan_num: int
    last_read_at: datetime
