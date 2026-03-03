"""Backfill existing cbeta_id values into text_identifiers table."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, text

from app.database import async_session
from app.models.source import DataSource, TextIdentifier
from app.models.text import BuddhistText


async def main():
    async with async_session() as session:
        # Get CBETA source
        result = await session.execute(
            select(DataSource).where(DataSource.code == "cbeta")
        )
        cbeta_source = result.scalar_one_or_none()
        if not cbeta_source:
            print("ERROR: CBETA data source not found. Run migration 0004 first.")
            return

        # Get all texts that don't yet have a CBETA identifier
        existing = await session.execute(
            select(TextIdentifier.text_id).where(TextIdentifier.source_id == cbeta_source.id)
        )
        existing_ids = {row[0] for row in existing.all()}

        result = await session.execute(select(BuddhistText))
        texts = result.scalars().all()

        count = 0
        for t in texts:
            if t.id in existing_ids:
                continue
            ident = TextIdentifier(
                text_id=t.id,
                source_id=cbeta_source.id,
                source_uid=t.cbeta_id,
                source_url=t.cbeta_url,
            )
            session.add(ident)
            count += 1

        await session.commit()
        print(f"Backfilled {count} CBETA identifiers.")


if __name__ == "__main__":
    asyncio.run(main())
