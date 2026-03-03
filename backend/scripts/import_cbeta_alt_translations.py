"""Auto-detect alternative translations (same title, different translator) and create relations."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, func
from app.database import async_session
from app.models.text import BuddhistText
from app.models.relation import TextRelation


async def main():
    async with async_session() as session:
        # Find titles that appear more than once (different translators)
        stmt = (
            select(BuddhistText.title_zh)
            .group_by(BuddhistText.title_zh)
            .having(func.count(BuddhistText.id) > 1)
        )
        result = await session.execute(stmt)
        duplicate_titles = [row[0] for row in result.all()]
        print(f"Found {len(duplicate_titles)} titles with multiple versions.")

        count = 0
        for title in duplicate_titles:
            result = await session.execute(
                select(BuddhistText)
                .where(BuddhistText.title_zh == title)
                .order_by(BuddhistText.id)
            )
            texts = result.scalars().all()

            # Create pairwise alt_translation relations
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    # Skip if same translator
                    if texts[i].translator and texts[i].translator == texts[j].translator:
                        continue

                    # Check if relation already exists
                    existing = await session.execute(
                        select(TextRelation).where(
                            TextRelation.text_a_id == texts[i].id,
                            TextRelation.text_b_id == texts[j].id,
                            TextRelation.relation_type == "alt_translation",
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    rel = TextRelation(
                        text_a_id=texts[i].id,
                        text_b_id=texts[j].id,
                        relation_type="alt_translation",
                        confidence=0.9,
                        source="auto:same_title",
                        note=f"Same title: {title}",
                    )
                    session.add(rel)
                    count += 1

        await session.commit()
        print(f"Created {count} alt_translation relations.")


if __name__ == "__main__":
    asyncio.run(main())
