from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BuddhistText(Base):
    __tablename__ = "buddhist_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taisho_id: Mapped[str | None] = mapped_column(String(50), index=True)
    cbeta_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title_zh: Mapped[str] = mapped_column(String(500), index=True)
    title_sa: Mapped[str | None] = mapped_column(String(500))
    title_bo: Mapped[str | None] = mapped_column(String(500))
    title_pi: Mapped[str | None] = mapped_column(String(500))
    translator: Mapped[str | None] = mapped_column(String(200))
    dynasty: Mapped[str | None] = mapped_column(String(50))
    fascicle_count: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[str | None] = mapped_column(String(100))
    subcategory: Mapped[str | None] = mapped_column(String(200))
    cbeta_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
