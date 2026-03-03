"""
Import DILA (Dharma Drum Institute of Liberal Arts) authority database.

DILA Authority DB provides standardized data for Buddhist persons,
places, and time periods. This script enhances existing KGEntity records
rather than creating new BuddhistText entries.

Usage:
    python scripts/import_dila_authority.py
    python scripts/import_dila_authority.py --type person
    python scripts/import_dila_authority.py --limit 100
"""

import argparse
import asyncio
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.base_importer import BaseImporter

from sqlalchemy import select
from app.models.knowledge_graph import KGEntity


DILA_BASE = "https://authority.dila.edu.tw"
DILA_API = f"{DILA_BASE}/api"


class DILAAuthorityImporter(BaseImporter):
    SOURCE_CODE = "dila"
    SOURCE_NAME_ZH = "DILA 权威数据库"
    SOURCE_NAME_EN = "Dharma Drum Institute of Liberal Arts Authority Database"
    SOURCE_BASE_URL = DILA_BASE
    SOURCE_API_URL = DILA_API
    SOURCE_DESCRIPTION = "法鼓文理学院佛学权威数据库，提供人名、地名、时代等规范数据"
    RATE_LIMIT_DELAY = 1.0

    def __init__(self, limit: int = 0, entity_type: str | None = None):
        super().__init__()
        self.limit = limit
        self.entity_type = entity_type

    async def fetch_authority_list(self, auth_type: str, offset: int = 0) -> list[dict]:
        """Fetch a page of authority entries from DILA API."""
        try:
            resp = await self.rate_limited_get(
                f"{DILA_API}/{auth_type}",
                params={"offset": offset, "limit": 100},
            )
            data = resp.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("results", data.get("data", []))
        except Exception as e:
            print(f"  API error for {auth_type}: {e}")
            return []

    async def import_persons(self, session):
        """Import or enhance person entities from DILA (idempotent).

        Uses O(1) dict-based lookup (by_dila + by_name) matching the
        same pattern as import_places for consistent, fast matching.
        """
        print("\n  Importing DILA person authority data...")

        # Pre-load existing person entities and build lookup indexes
        result = await session.execute(
            select(KGEntity)
            .where(KGEntity.entity_type == "person")
            .order_by(KGEntity.id)
        )
        existing = list(result.scalars().all())
        by_dila: dict[str, KGEntity] = {}
        by_name: dict[str, KGEntity] = {}
        for e in existing:
            if e.external_ids and e.external_ids.get("dila"):
                by_dila[e.external_ids["dila"]] = e
            if e.name_zh:
                by_name[e.name_zh] = e
        print(f"  Found {len(existing)} existing person entities to enhance.")

        # Try to fetch DILA person data
        offset = 0
        enhanced = 0
        created = 0

        while True:
            persons = await self.fetch_authority_list("person", offset)
            if not persons:
                break

            for person in persons:
                dila_id = person.get("id", person.get("authority_id", ""))
                name_zh = person.get("name_zh", person.get("name", ""))
                name_sa = person.get("name_sa", person.get("sanskrit_name", ""))
                name_pi = person.get("name_pi", person.get("pali_name", ""))
                name_en = person.get("name_en", person.get("english_name", ""))
                dates = person.get("dates", person.get("time_period", ""))
                description = person.get("description", "")

                if not name_zh:
                    continue

                # Match: prefer dila_id, fallback to name_zh
                entity = None
                if dila_id:
                    entity = by_dila.get(dila_id)
                if entity is None:
                    entity = by_name.get(name_zh)

                if entity is not None:
                    # Enhance existing entity (only fill blanks)
                    changed = False
                    if name_sa and not entity.name_sa:
                        entity.name_sa = name_sa
                        changed = True
                    if name_pi and not entity.name_pi:
                        entity.name_pi = name_pi
                        changed = True
                    if name_en and not entity.name_en:
                        entity.name_en = name_en
                        changed = True
                    if description and not entity.description:
                        entity.description = description
                        changed = True

                    # Always merge external_ids with DILA authority ID
                    if dila_id:
                        ext_ids = dict(entity.external_ids or {})
                        if ext_ids.get("dila") != dila_id:
                            ext_ids["dila"] = dila_id
                            entity.external_ids = ext_ids
                            by_dila[dila_id] = entity
                            changed = True

                    if changed:
                        enhanced += 1
                else:
                    # Create new KG entity for persons not yet in DB
                    if self.limit and (enhanced + created) >= self.limit:
                        break

                    ext_ids = {"dila": dila_id} if dila_id else None
                    new_entity = KGEntity(
                        entity_type="person",
                        name_zh=name_zh,
                        name_sa=name_sa or None,
                        name_pi=name_pi or None,
                        name_en=name_en or None,
                        description=description or None,
                        external_ids=ext_ids,
                    )
                    session.add(new_entity)
                    # Register in lookup indexes for intra-batch dedup
                    by_name[name_zh] = new_entity
                    if dila_id:
                        by_dila[dila_id] = new_entity
                    created += 1

            offset += len(persons)
            await session.flush()
            print(f"  Processed {offset} DILA persons, enhanced {enhanced}, created {created}...")

            if self.limit and (enhanced + created) >= self.limit:
                break

            if len(persons) < 100:
                break

        self.stats.texts_updated = enhanced + created
        print(f"  Person import done: {enhanced} enhanced, {created} created.")

    async def import_places(self, session):
        """Import or enhance place entities from DILA (idempotent)."""
        print("\n  Importing DILA place authority data...")

        # Pre-load existing place entities for dedup
        result = await session.execute(
            select(KGEntity)
            .where(KGEntity.entity_type == "place")
            .order_by(KGEntity.id)
        )
        existing = list(result.scalars().all())
        # Build lookup indexes: dila_id -> entity, name_zh -> entity
        by_dila: dict[str, KGEntity] = {}
        by_name: dict[str, KGEntity] = {}
        for e in existing:
            if e.external_ids and e.external_ids.get("dila"):
                by_dila[e.external_ids["dila"]] = e
            by_name[e.name_zh] = e
        print(f"  Found {len(existing)} existing place entities.")

        offset = 0
        enhanced = 0
        created = 0

        while True:
            places = await self.fetch_authority_list("place", offset)
            if not places:
                break

            for place in places:
                dila_id = place.get("id", place.get("authority_id", ""))
                name_zh = place.get("name_zh", place.get("name", ""))
                name_sa = place.get("name_sa", "")
                name_en = place.get("name_en", "")
                description = place.get("description", "")

                if not name_zh:
                    continue

                # Match: prefer dila_id, fallback to name_zh
                entity = None
                if dila_id:
                    entity = by_dila.get(dila_id)
                if entity is None:
                    entity = by_name.get(name_zh)

                if entity is not None:
                    # Enhance existing entity
                    changed = False
                    if name_sa and not entity.name_sa:
                        entity.name_sa = name_sa
                        changed = True
                    if name_en and not entity.name_en:
                        entity.name_en = name_en
                        changed = True
                    if description and not entity.description:
                        entity.description = description
                        changed = True
                    if dila_id:
                        ext_ids = dict(entity.external_ids or {})
                        if ext_ids.get("dila") != dila_id:
                            ext_ids["dila"] = dila_id
                            entity.external_ids = ext_ids
                            by_dila[dila_id] = entity
                            changed = True
                    if changed:
                        enhanced += 1
                else:
                    # Create new place entity
                    ext_ids = {"dila": dila_id} if dila_id else None
                    new_entity = KGEntity(
                        entity_type="place",
                        name_zh=name_zh,
                        name_sa=name_sa or None,
                        name_en=name_en or None,
                        description=description or None,
                        external_ids=ext_ids,
                    )
                    session.add(new_entity)
                    # Register in lookup indexes for intra-batch dedup
                    by_name[name_zh] = new_entity
                    if dila_id:
                        by_dila[dila_id] = new_entity
                    created += 1

            offset += len(places)
            await session.flush()

            if self.limit and (enhanced + created) >= self.limit:
                break
            if len(places) < 100:
                break

        print(f"  Place import done: {enhanced} enhanced, {created} created.")

    async def run_import(self):
        async with self.session_factory() as session:
            await self.ensure_source(session)

            if self.entity_type in (None, "person"):
                await self.import_persons(session)

            if self.entity_type in (None, "place"):
                await self.import_places(session)

            await session.commit()


async def main():
    parser = argparse.ArgumentParser(description="Import DILA authority data")
    parser.add_argument("--limit", type=int, default=0, help="Limit per entity type")
    parser.add_argument("--type", dest="entity_type", choices=["person", "place"],
                        help="Import only specific entity type")
    args = parser.parse_args()

    importer = DILAAuthorityImporter(limit=args.limit, entity_type=args.entity_type)
    await importer.execute()


if __name__ == "__main__":
    asyncio.run(main())
