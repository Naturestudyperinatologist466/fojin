from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TextRelation(Base):
    __tablename__ = "text_relations"
    __table_args__ = (
        UniqueConstraint("text_a_id", "text_b_id", "relation_type", name="uq_text_relation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_a_id: Mapped[int] = mapped_column(Integer, ForeignKey("buddhist_texts.id"), index=True)
    text_b_id: Mapped[int] = mapped_column(Integer, ForeignKey("buddhist_texts.id"), index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # parallel, alt_translation, commentary
    confidence: Mapped[float] = mapped_column(Float, server_default="1.0")
    source: Mapped[str | None] = mapped_column(String(200))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    text_a: Mapped["BuddhistText"] = relationship(foreign_keys=[text_a_id])  # noqa: F821
    text_b: Mapped["BuddhistText"] = relationship(foreign_keys=[text_b_id])  # noqa: F821
