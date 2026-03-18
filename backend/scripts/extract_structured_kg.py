"""
Structured Knowledge Graph Extraction from Buddhist Text Metadata.

Idempotent extractor — safe to run repeatedly (upsert semantics).
Entity dedup: (entity_type, name_zh) for person/dynasty; (entity_type, text_id) for text.
Relation dedup: (subject_id, predicate, object_id, source) enforced by partial unique index.

Passes:
  A — Upsert person / dynasty / text entities from buddhist_texts
  B — Build translated / active_in relations
  C — Sync alt_translation relations from text_relations → KG
  D — Sync parallel + commentary from text_relations → KG
  E — Extract citations from CBETA XML <note type="cf*"> tags
  F — Detect commentary relations by title suffix patterns

Usage:
    python scripts/extract_structured_kg.py
    python scripts/extract_structured_kg.py --pass A
    python scripts/extract_structured_kg.py --pass D
    python scripts/extract_structured_kg.py --pass E --dry-run
    python scripts/extract_structured_kg.py --pass F --dry-run
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.database import async_session
from app.models.knowledge_graph import KGEntity, KGRelation
from app.models.relation import TextRelation
from app.models.source import DataSource, TextIdentifier
from app.models.text import BuddhistText

# ── Source tags — every auto-generated relation records its provenance ──
SOURCE_CBETA = "auto:cbeta_metadata"
SOURCE_ALT_TRANS = "auto:alt_translation"
SOURCE_TEXT_REL_SYNC = "auto:text_relation_sync"
SOURCE_CBETA_CF = "auto:cbeta_cf_note"
SOURCE_TITLE_PATTERN = "auto:title_pattern"
SOURCE_CONCEPT_MATCH = "auto:concept_title_match"

BATCH_SIZE = 500


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

async def load_entity_map(session, entity_type: str, key: str = "name_zh") -> dict:
    """Load existing entities of a type into {key_value: entity_id} map."""
    result = await session.execute(
        select(KGEntity).where(KGEntity.entity_type == entity_type)
    )
    entities = result.scalars().all()
    if key == "text_id":
        return {e.text_id: e.id for e in entities if e.text_id is not None}
    return {e.name_zh: e.id for e in entities}


async def load_relation_keys(session, source: str) -> set[tuple[int, str, int]]:
    """Load existing relations for a given source as {(subject_id, predicate, object_id)}."""
    result = await session.execute(
        select(KGRelation.subject_id, KGRelation.predicate, KGRelation.object_id)
        .where(KGRelation.source == source)
    )
    return {(r[0], r[1], r[2]) for r in result.all()}


async def load_84000_identifier_map(session) -> dict[int, tuple[str, str | None]]:
    """Load 84000 identifiers as {text_id: (source_uid, source_url)}."""
    result = await session.execute(
        select(TextIdentifier.text_id, TextIdentifier.source_uid, TextIdentifier.source_url)
        .join(TextIdentifier.source)
        .where(DataSource.code == "84000")
        .order_by(TextIdentifier.id)
    )
    id_map: dict[int, tuple[str, str | None]] = {}
    for text_id, source_uid, source_url in result.all():
        if text_id not in id_map:
            id_map[text_id] = (source_uid, source_url)
    return id_map


def extract_toh_number(source_uid: str | None) -> str | None:
    """Extract normalized numeric Toh identifier from source_uid like 'toh44'."""
    if not source_uid:
        return None
    match = re.search(r"(\d+(?:-\d+)?)", source_uid)
    return match.group(1) if match else None


# ═══════════════════════════════════════════════════════════════════
# Pass A: Upsert entities
# ═══════════════════════════════════════════════════════════════════

async def upsert_person_entities(session, person_map: dict[str, int]) -> int:
    """Create person entities from unique translators in buddhist_texts.

    Dedup key: (entity_type='person', name_zh=translator).
    Only creates entities for translators not yet in person_map.
    """
    result = await session.execute(
        select(BuddhistText.translator, BuddhistText.dynasty)
        .where(BuddhistText.translator.isnot(None), BuddhistText.translator != "")
        .group_by(BuddhistText.translator, BuddhistText.dynasty)
    )
    rows = result.all()

    created = 0
    seen: set[str] = set()  # deduplicate within this run (same translator, multiple dynasties)
    for translator, dynasty in rows:
        if not translator or translator in person_map or translator in seen:
            continue
        seen.add(translator)

        entity = KGEntity(
            entity_type="person",
            name_zh=translator,
            description="佛典译者" + (f"，{dynasty}" if dynasty else ""),
            properties={"role": "translator", **({"dynasty": dynasty} if dynasty else {})},
        )
        session.add(entity)
        await session.flush()
        person_map[translator] = entity.id
        created += 1

    return created


async def upsert_dynasty_entities(session, dynasty_map: dict[str, int]) -> int:
    """Create dynasty entities from unique dynasties in buddhist_texts.

    Dedup key: (entity_type='dynasty', name_zh=dynasty).
    """
    result = await session.execute(
        select(BuddhistText.dynasty)
        .where(BuddhistText.dynasty.isnot(None), BuddhistText.dynasty != "")
        .group_by(BuddhistText.dynasty)
    )
    dynasties = [row[0] for row in result.all()]

    created = 0
    for name in dynasties:
        if name in dynasty_map:
            continue
        entity = KGEntity(
            entity_type="dynasty",
            name_zh=name,
            description=f"中国朝代：{name}",
        )
        session.add(entity)
        await session.flush()
        dynasty_map[name] = entity.id
        created += 1

    return created


async def upsert_text_entities(session, text_map: dict[int, int]) -> tuple[int, int]:
    """Create or enrich text entities from buddhist_texts.

    Dedup key: (entity_type='text', text_id=BuddhistText.id).
    Creates missing entities and backfills existing ones with multilingual titles
    plus 84000 identifiers / Toh numbers where available.
    """
    existing_result = await session.execute(
        select(KGEntity)
        .where(KGEntity.entity_type == "text", KGEntity.text_id.isnot(None))
        .order_by(KGEntity.id)
    )
    existing_entities = {
        entity.text_id: entity
        for entity in existing_result.scalars().all()
        if entity.text_id is not None
    }
    id_84000_map = await load_84000_identifier_map(session)

    offset = 0
    created = 0
    updated = 0

    while True:
        result = await session.execute(
            select(BuddhistText)
            .order_by(BuddhistText.id)
            .offset(offset)
            .limit(BATCH_SIZE)
        )
        texts = result.scalars().all()
        if not texts:
            break

        batch_new: list[tuple[int, KGEntity]] = []
        for t in texts:
            source_uid, _source_url = id_84000_map.get(t.id, (None, None))
            toh_number = extract_toh_number(source_uid)

            entity = existing_entities.get(t.id)
            if entity is not None:
                changed = False
                if t.title_sa and not entity.name_sa:
                    entity.name_sa = t.title_sa
                    changed = True
                if t.title_bo and not entity.name_bo:
                    entity.name_bo = t.title_bo
                    changed = True
                if t.title_pi and not entity.name_pi:
                    entity.name_pi = t.title_pi
                    changed = True
                if t.title_en and not entity.name_en:
                    entity.name_en = t.title_en
                    changed = True

                props = dict(entity.properties or {})
                if t.cbeta_id and props.get("cbeta_id") != t.cbeta_id:
                    props["cbeta_id"] = t.cbeta_id
                    changed = True
                if toh_number and props.get("toh_number") != toh_number:
                    props["toh_number"] = toh_number
                    changed = True
                if changed:
                    entity.properties = props or None

                if source_uid:
                    ext_ids = dict(entity.external_ids or {})
                    if ext_ids.get("84000") != source_uid:
                        ext_ids["84000"] = source_uid
                        entity.external_ids = ext_ids
                        changed = True

                if changed:
                    updated += 1
                continue

            properties = {}
            if t.cbeta_id:
                properties["cbeta_id"] = t.cbeta_id
            if toh_number:
                properties["toh_number"] = toh_number

            external_ids = {"84000": source_uid} if source_uid else None
            entity = KGEntity(
                entity_type="text",
                name_zh=t.title_zh,
                name_sa=t.title_sa,
                name_bo=t.title_bo,
                name_pi=t.title_pi,
                name_en=t.title_en,
                text_id=t.id,
                properties=properties or None,
                external_ids=external_ids,
            )
            session.add(entity)
            batch_new.append((t.id, entity))

        if batch_new:
            await session.flush()
            for text_id, entity in batch_new:
                text_map[text_id] = entity.id
                existing_entities[text_id] = entity
            created += len(batch_new)
        elif texts:
            await session.flush()

        offset += len(texts)
        if len(texts) < BATCH_SIZE:
            break

    return created, updated


# ═══════════════════════════════════════════════════════════════════
# Pass B: Build core relations from CBETA metadata
# ═══════════════════════════════════════════════════════════════════

async def build_translated_relations(
    session,
    person_map: dict[str, int],
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Create 'translated' relations: person → text.

    Source: auto:cbeta_metadata. Confidence: 1.0.
    """
    offset = 0
    created = 0

    while True:
        result = await session.execute(
            select(BuddhistText.id, BuddhistText.translator)
            .where(BuddhistText.translator.isnot(None), BuddhistText.translator != "")
            .order_by(BuddhistText.id)
            .offset(offset)
            .limit(BATCH_SIZE)
        )
        rows = result.all()
        if not rows:
            break

        for text_id, translator in rows:
            person_id = person_map.get(translator)
            text_entity_id = text_map.get(text_id)
            if not person_id or not text_entity_id:
                continue
            key = (person_id, "translated", text_entity_id)
            if key in existing:
                continue
            session.add(KGRelation(
                subject_id=person_id,
                predicate="translated",
                object_id=text_entity_id,
                source=SOURCE_CBETA,
                confidence=1.0,
            ))
            existing.add(key)
            created += 1

        await session.flush()
        offset += len(rows)
        if len(rows) < BATCH_SIZE:
            break

    return created


async def build_active_in_relations(
    session,
    person_map: dict[str, int],
    dynasty_map: dict[str, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Create 'active_in' relations: person → dynasty.

    Source: auto:cbeta_metadata. Confidence: 1.0.
    One relation per unique (translator, dynasty) pair.
    """
    result = await session.execute(
        select(BuddhistText.translator, BuddhistText.dynasty)
        .where(
            BuddhistText.translator.isnot(None), BuddhistText.translator != "",
            BuddhistText.dynasty.isnot(None), BuddhistText.dynasty != "",
        )
        .group_by(BuddhistText.translator, BuddhistText.dynasty)
    )
    rows = result.all()

    created = 0
    for translator, dynasty in rows:
        person_id = person_map.get(translator)
        dynasty_id = dynasty_map.get(dynasty)
        if not person_id or not dynasty_id:
            continue
        key = (person_id, "active_in", dynasty_id)
        if key in existing:
            continue
        session.add(KGRelation(
            subject_id=person_id,
            predicate="active_in",
            object_id=dynasty_id,
            source=SOURCE_CBETA,
            confidence=1.0,
        ))
        existing.add(key)
        created += 1

    await session.flush()
    return created


# ═══════════════════════════════════════════════════════════════════
# Pass C: Sync alt_translation from text_relations into KG
# ═══════════════════════════════════════════════════════════════════

async def build_alt_translation_relations(
    session,
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Sync alt_translation rows from text_relations → KG relations.

    Source: auto:alt_translation. Confidence: inherited from text_relations.
    """
    offset = 0
    created = 0

    while True:
        result = await session.execute(
            select(TextRelation)
            .where(TextRelation.relation_type == "alt_translation")
            .order_by(TextRelation.id)
            .offset(offset)
            .limit(BATCH_SIZE)
        )
        rels = result.scalars().all()
        if not rels:
            break

        for r in rels:
            entity_a = text_map.get(r.text_a_id)
            entity_b = text_map.get(r.text_b_id)
            if not entity_a or not entity_b:
                continue
            key = (entity_a, "alt_translation", entity_b)
            if key in existing:
                continue
            session.add(KGRelation(
                subject_id=entity_a,
                predicate="alt_translation",
                object_id=entity_b,
                source=SOURCE_ALT_TRANS,
                confidence=r.confidence or 0.9,
            ))
            existing.add(key)
            created += 1

        await session.flush()
        offset += len(rels)
        if len(rels) < BATCH_SIZE:
            break

    return created


# ═══════════════════════════════════════════════════════════════════
# Pass D: Sync parallel + commentary from text_relations into KG
# ═══════════════════════════════════════════════════════════════════

async def build_parallel_relations(
    session,
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Sync parallel rows from text_relations → KG relations.

    Source: auto:text_relation_sync. Confidence: inherited from text_relations.
    """
    offset = 0
    created = 0

    while True:
        result = await session.execute(
            select(TextRelation)
            .where(TextRelation.relation_type == "parallel")
            .order_by(TextRelation.id)
            .offset(offset)
            .limit(BATCH_SIZE)
        )
        rels = result.scalars().all()
        if not rels:
            break

        for r in rels:
            entity_a = text_map.get(r.text_a_id)
            entity_b = text_map.get(r.text_b_id)
            if not entity_a or not entity_b:
                continue
            key = (entity_a, "parallel_text", entity_b)
            if key in existing:
                continue
            session.add(KGRelation(
                subject_id=entity_a,
                predicate="parallel_text",
                object_id=entity_b,
                source=SOURCE_TEXT_REL_SYNC,
                confidence=r.confidence or 0.8,
            ))
            existing.add(key)
            created += 1

        await session.flush()
        offset += len(rels)
        if len(rels) < BATCH_SIZE:
            break

    return created


async def build_commentary_from_text_relations(
    session,
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Sync commentary rows from text_relations → KG relations.

    Source: auto:text_relation_sync. Confidence: inherited from text_relations.
    """
    offset = 0
    created = 0

    while True:
        result = await session.execute(
            select(TextRelation)
            .where(TextRelation.relation_type == "commentary")
            .order_by(TextRelation.id)
            .offset(offset)
            .limit(BATCH_SIZE)
        )
        rels = result.scalars().all()
        if not rels:
            break

        for r in rels:
            entity_a = text_map.get(r.text_a_id)
            entity_b = text_map.get(r.text_b_id)
            if not entity_a or not entity_b:
                continue
            # text_a is the commentary, text_b is the root text
            key = (entity_a, "commentary_on", entity_b)
            if key in existing:
                continue
            session.add(KGRelation(
                subject_id=entity_a,
                predicate="commentary_on",
                object_id=entity_b,
                source=SOURCE_TEXT_REL_SYNC,
                confidence=r.confidence or 0.8,
            ))
            existing.add(key)
            created += 1

        await session.flush()
        offset += len(rels)
        if len(rels) < BATCH_SIZE:
            break

    return created


# ═══════════════════════════════════════════════════════════════════
# Pass E: Extract citations from CBETA XML <note type="cf*"> tags
# ═══════════════════════════════════════════════════════════════════

# Regex to extract a CBETA-style text reference from cf note content.
# Matches patterns like T30n1564_p0040c16, X23n0443_p0709c16
# Captures: collection letter(s) + text number  e.g. ("T", "1564")
_CF_REF_RE = re.compile(r"([A-Z]+)\d+n(\d+)")


def _cbeta_id_from_ref(collection: str, number: str) -> str:
    """Build a cbeta_id-like key from collection and number: e.g. 'T1564'."""
    return f"{collection}{number}"


async def _load_cbeta_id_to_entity(session) -> dict[str, int]:
    """Build {cbeta_id_prefix: entity_id} map.

    For each text entity we extract the collection+number prefix from the cbeta_id
    property (e.g. "T0001" from "T0001_.01.0001a01") to allow matching against
    citation references.
    """
    result = await session.execute(
        select(KGEntity.id, KGEntity.properties)
        .where(KGEntity.entity_type == "text", KGEntity.properties.isnot(None))
    )
    cbeta_map: dict[str, int] = {}
    for entity_id, props in result.all():
        cbeta_id = (props or {}).get("cbeta_id")
        if not cbeta_id:
            continue
        # Extract collection+number prefix, e.g. "T0001" from "T0001_.01..."
        m = re.match(r"([A-Z]+)(\d+)", cbeta_id)
        if m:
            # Normalize: strip leading zeros for matching
            prefix = f"{m.group(1)}{int(m.group(2))}"
            cbeta_map[prefix] = entity_id
    return cbeta_map


def _extract_source_cbeta_prefix(xml_path: Path) -> str | None:
    """Extract normalized cbeta prefix from filename like T39n1803.xml → 'T1803'."""
    m = re.match(r"([A-Z]+)\d+n(\d+)", xml_path.stem)
    if m:
        return f"{m.group(1)}{int(m.group(2))}"
    return None


async def extract_cbeta_citations(
    session,
    existing: set[tuple[int, str, int]],
    dry_run: bool = False,
) -> int:
    """Parse CBETA XML files for <note type="cf*"> cross-references.

    Creates 'cites' relations between texts.  Deduplicates by
    (source_entity, "cites", target_entity) pairs — multiple page-level
    references between the same two works collapse into one relation.

    Source: auto:cbeta_cf_note.  Confidence: 0.7.
    """
    from lxml import etree

    TEI_NS = "{http://www.tei-c.org/ns/1.0}"
    xml_root = Path(__file__).resolve().parents[1] / "data" / "xml-p5"
    if not xml_root.exists():
        print(f"  [SKIP] XML data directory not found: {xml_root}")
        return 0

    cbeta_map = await _load_cbeta_id_to_entity(session)
    print(f"  cbeta_id map loaded: {len(cbeta_map)} entries")

    created = 0
    files_processed = 0
    batch_new: list[KGRelation] = []

    for xml_file in sorted(xml_root.rglob("*.xml")):
        source_prefix = _extract_source_cbeta_prefix(xml_file)
        if not source_prefix:
            continue
        source_entity = cbeta_map.get(source_prefix)
        if source_entity is None:
            continue

        try:
            tree = etree.parse(str(xml_file))
        except etree.XMLSyntaxError:
            continue

        files_processed += 1

        # Find all <note type="cf*"> elements (TEI namespace)
        for note_el in tree.iter(f"{TEI_NS}note"):
            note_type = note_el.get("type", "")
            if not note_type.startswith("cf"):
                continue
            text_content = (note_el.text or "").strip()
            if not text_content:
                continue

            m = _CF_REF_RE.match(text_content)
            if not m:
                continue

            target_prefix = _cbeta_id_from_ref(m.group(1), str(int(m.group(2))))
            target_entity = cbeta_map.get(target_prefix)
            if target_entity is None or target_entity == source_entity:
                continue

            key = (source_entity, "cites", target_entity)
            if key in existing:
                continue

            batch_new.append(KGRelation(
                subject_id=source_entity,
                predicate="cites",
                object_id=target_entity,
                source=SOURCE_CBETA_CF,
                confidence=0.7,
                properties={
                    "evidence_file": xml_file.name,
                    "evidence_note": text_content[:100],
                    "evidence_target_ref": target_prefix,
                },
            ))
            existing.add(key)
            created += 1

        # Flush in batches
        if len(batch_new) >= BATCH_SIZE:
            for rel in batch_new:
                session.add(rel)
            await session.flush()
            batch_new.clear()

    # Flush remainder
    if batch_new:
        for rel in batch_new:
            session.add(rel)
        await session.flush()
        batch_new.clear()

    print(f"  XML files processed: {files_processed}")
    return created


# ═══════════════════════════════════════════════════════════════════
# Pass F: Detect commentary relations from title patterns
# ═══════════════════════════════════════════════════════════════════

# Commentary-indicating suffixes in Chinese Buddhist text titles
_COMMENTARY_SUFFIXES = [
    "演義鈔", "玄義", "文句", "述記", "義疏",
    "疏", "注", "記", "鈔", "解",
]
# Pre-compiled pattern: match any suffix at end of title
_COMMENTARY_SUFFIX_RE = re.compile(
    r"(.+?)(" + "|".join(re.escape(s) for s in _COMMENTARY_SUFFIXES) + r")$"
)

# False positive filter — titles ending in 記 that are NOT commentaries
_FALSE_POSITIVE_RE = re.compile(
    r"(授記|集驗記|傳記|感應記|往生記|遊行記|果記|錄|本事記|遊方記|感通記"
    r"|行記|別記|聞記|內傳|外傳|高僧傳|求法傳|西域記|雜記|名僧傳)"
)

# Common abbreviations used in commentary titles → full root text name
_ABBREVIATIONS: dict[str, str] = {
    "法華": "妙法蓮華經",
    "華嚴": "大方廣佛華嚴經",
    "金剛經": "金剛般若波羅蜜經",
    "心經": "般若波羅蜜多心經",
    "涅槃": "大般涅槃經",
    "維摩": "維摩詰所說經",
    "楞嚴": "大佛頂如來密因修證了義諸菩薩萬行首楞嚴經",
    "圓覺": "大方廣圓覺修多羅了義經",
    "楞伽": "楞伽阿跋多羅寶經",
    "般若": "大般若波羅蜜多經",
    "阿彌陀": "佛說阿彌陀經",
    "藥師": "藥師琉璃光如來本願功德經",
    "地藏": "地藏菩薩本願經",
    "金光明": "金光明最勝王經",
    "仁王": "仁王護國般若波羅蜜多經",
    "無量壽": "佛說無量壽經",
    "觀無量壽": "佛說觀無量壽佛經",
    "十地": "十地經論",
    "成唯識": "成唯識論",
    "瑜伽": "瑜伽師地論",
    "俱舍": "阿毘達磨俱舍論",
    "中論": "中論",
    "百論": "百論",
    "十二門": "十二門論",
    "大智度": "大智度論",
}


async def detect_commentary_by_title(
    session,
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Detect commentary relationships by matching title suffixes.

    If a text's title ends with a commentary suffix (疏/注/記/鈔/…),
    strip the suffix and search for a matching root text.
    Creates 'commentary_on' relations with confidence 0.8 (exact) or 0.6 (fuzzy).

    Source: auto:title_pattern.
    """
    # Load all text entities with their names
    result = await session.execute(
        select(KGEntity.id, KGEntity.name_zh, KGEntity.text_id)
        .where(KGEntity.entity_type == "text")
    )
    all_texts = result.all()

    # Build lookup: name_zh → entity_id (for root text matching)
    name_to_entity: dict[str, int] = {}
    for eid, name, _ in all_texts:
        if name:
            name_to_entity[name] = eid

    created = 0
    batch_new: list[KGRelation] = []

    for entity_id, name_zh, _text_id in all_texts:
        if not name_zh:
            continue
        # Skip false positives (titles that contain 記 but aren't commentaries)
        if _FALSE_POSITIVE_RE.search(name_zh):
            continue
        m = _COMMENTARY_SUFFIX_RE.match(name_zh)
        if not m:
            continue

        root_name = m.group(1).strip()
        if not root_name:
            continue

        suffix = m.group(2)
        match_method = None
        root_name_matched = None

        # Exact match
        root_entity = name_to_entity.get(root_name)
        confidence = 0.8
        if root_entity is not None:
            match_method = "exact"
            root_name_matched = root_name

        # Abbreviation lookup
        if root_entity is None:
            full_name = _ABBREVIATIONS.get(root_name)
            if full_name:
                root_entity = name_to_entity.get(full_name)
                if root_entity is not None:
                    confidence = 0.7
                    match_method = "abbreviation"
                    root_name_matched = full_name

        # Fuzzy: try adding common prefixes/suffixes
        if root_entity is None:
            for variant in [f"大方廣{root_name}", f"{root_name}經", f"妙法{root_name}"]:
                root_entity = name_to_entity.get(variant)
                if root_entity is not None:
                    confidence = 0.6
                    match_method = "prefix_suffix"
                    root_name_matched = variant
                    break

        # LIKE fuzzy fallback — only if unique match
        if root_entity is None:
            candidates = [
                eid for name, eid in name_to_entity.items()
                if root_name in name and eid != entity_id
            ]
            if len(candidates) == 1:
                root_entity = candidates[0]
                confidence = 0.5
                match_method = "contains_unique"
                root_name_matched = root_name

        if root_entity is None or root_entity == entity_id:
            continue

        key = (entity_id, "commentary_on", root_entity)
        if key in existing:
            continue

        batch_new.append(KGRelation(
            subject_id=entity_id,
            predicate="commentary_on",
            object_id=root_entity,
            source=SOURCE_TITLE_PATTERN,
            confidence=confidence,
            properties={
                "evidence_rule": f"suffix:{suffix}",
                "evidence_source_title": name_zh,
                "evidence_root_title": root_name_matched or root_name,
                "evidence_match_method": match_method or "unknown",
            },
        ))
        existing.add(key)
        created += 1

    if batch_new:
        for rel in batch_new:
            session.add(rel)
        await session.flush()

    return created


# ═══════════════════════════════════════════════════════════════════
# Pass G: Link texts to concept entities by title keywords
# ═══════════════════════════════════════════════════════════════════

# Concept name → keywords that trigger the association.
# Each keyword is checked against text titles; if found, the text
# gets an "associated_with" relation to the concept entity.
_CONCEPT_KEYWORDS: dict[str, list[str]] = {
    "缘起": ["缘起", "緣起", "因缘", "因緣"],
    "四圣谛": ["四谛", "四諦", "圣谛", "聖諦"],
    "八正道": ["八正道", "八聖道"],
    "空性": ["般若波罗蜜", "般若波羅蜜", "空性"],
    "唯识": ["唯识", "唯識", "瑜伽师地", "瑜伽師地", "成唯識", "成唯识"],
    "佛性": ["如来藏", "如來藏", "佛性"],
    "般若": ["般若"],
    "涅槃": ["涅槃", "涅盤"],
    "菩提": ["菩提"],
    "三法印": ["三法印"],
    "十二因缘": ["十二因缘", "十二因緣", "十二缘", "十二緣"],
    "六波罗蜜": ["波罗蜜", "波羅蜜"],
    "中道": ["中论", "中論", "中道"],
    "三学": ["三学", "三學"],
    "五蕴": ["五蕴", "五蘊", "五陰"],
    "禅定": ["禅定", "禪定", "坐禅", "坐禪"],
    "业": ["业报", "業報", "因果"],
    "轮回": ["轮回", "輪迴", "六道"],
}


async def link_texts_to_concepts(
    session,
    text_map: dict[int, int],
    existing: set[tuple[int, str, int]],
) -> int:
    """Link text entities to concept entities by title keyword matching.

    For each concept entity, search text titles for associated keywords.
    Creates 'associated_with' relations with confidence 0.7.
    Source: auto:concept_title_match.
    """
    # Load concept entities
    concept_result = await session.execute(
        select(KGEntity.id, KGEntity.name_zh)
        .where(KGEntity.entity_type == "concept")
    )
    concept_map = {name: eid for eid, name in concept_result.all()}
    if not concept_map:
        print("  No concept entities found, skipping.")
        return 0

    # Load all text entities with titles
    text_result = await session.execute(
        select(KGEntity.id, KGEntity.name_zh)
        .where(KGEntity.entity_type == "text", KGEntity.name_zh.isnot(None))
    )
    all_texts = text_result.all()

    created = 0
    batch_new: list[KGRelation] = []

    for concept_name, keywords in _CONCEPT_KEYWORDS.items():
        concept_id = concept_map.get(concept_name)
        if concept_id is None:
            continue

        for text_entity_id, title in all_texts:
            if not title:
                continue
            if not any(kw in title for kw in keywords):
                continue

            key = (text_entity_id, "associated_with", concept_id)
            if key in existing:
                continue

            batch_new.append(KGRelation(
                subject_id=text_entity_id,
                predicate="associated_with",
                object_id=concept_id,
                source=SOURCE_CONCEPT_MATCH,
                confidence=0.7,
                properties={
                    "evidence_rule": f"title_keyword:{concept_name}",
                    "evidence_source_title": title,
                },
            ))
            existing.add(key)
            created += 1

    if batch_new:
        for rel in batch_new:
            session.add(rel)
        await session.flush()

    return created


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

async def run(run_pass: str | None = None, dry_run: bool = False):
    run_all = run_pass is None

    print("=" * 60)
    print("佛津 (FoJin) — Structured KG Extraction")
    print("=" * 60)

    async with async_session() as session:
        # Load existing entity maps
        print("\nLoading existing KG data...")
        person_map = await load_entity_map(session, "person", "name_zh")
        dynasty_map = await load_entity_map(session, "dynasty", "name_zh")
        text_map = await load_entity_map(session, "text", "text_id")
        print(f"  Existing: {len(person_map)} persons, "
              f"{len(dynasty_map)} dynasties, {len(text_map)} texts")

        # ── Pass A ──
        if run_all or run_pass == "A":
            print("\n── Pass A: Upsert entities ──")
            p = await upsert_person_entities(session, person_map)
            print(f"  Persons:   +{p} (total {len(person_map)})")
            d = await upsert_dynasty_entities(session, dynasty_map)
            print(f"  Dynasties: +{d} (total {len(dynasty_map)})")
            t_created, t_updated = await upsert_text_entities(session, text_map)
            print(f"  Texts:     +{t_created} created, +{t_updated} enriched (total {len(text_map)})")

        # ── Pass B ──
        if run_all or run_pass == "B":
            print("\n── Pass B: Build relations (cbeta_metadata) ──")
            cbeta_rels = await load_relation_keys(session, SOURCE_CBETA)
            print(f"  Existing {SOURCE_CBETA} relations: {len(cbeta_rels)}")
            tr = await build_translated_relations(
                session, person_map, text_map, cbeta_rels)
            print(f"  translated: +{tr}")
            ai = await build_active_in_relations(
                session, person_map, dynasty_map, cbeta_rels)
            print(f"  active_in:  +{ai}")

        # ── Pass C ──
        if run_all or run_pass == "C":
            print("\n── Pass C: Sync alt_translation → KG ──")
            alt_rels = await load_relation_keys(session, SOURCE_ALT_TRANS)
            print(f"  Existing {SOURCE_ALT_TRANS} relations: {len(alt_rels)}")
            at = await build_alt_translation_relations(
                session, text_map, alt_rels)
            print(f"  alt_translation: +{at}")

        # ── Pass D ──
        if run_all or run_pass == "D":
            print("\n── Pass D: Sync parallel + commentary text_relations → KG ──")
            sync_rels = await load_relation_keys(session, SOURCE_TEXT_REL_SYNC)
            print(f"  Existing {SOURCE_TEXT_REL_SYNC} relations: {len(sync_rels)}")
            pt = await build_parallel_relations(session, text_map, sync_rels)
            print(f"  parallel_text:  +{pt}")
            co = await build_commentary_from_text_relations(
                session, text_map, sync_rels)
            print(f"  commentary_on:  +{co}")

        # ── Pass E ──
        if run_all or run_pass == "E":
            print("\n── Pass E: Extract CBETA XML citations ──")
            cf_rels = await load_relation_keys(session, SOURCE_CBETA_CF)
            print(f"  Existing {SOURCE_CBETA_CF} relations: {len(cf_rels)}")
            ci = await extract_cbeta_citations(session, cf_rels, dry_run=dry_run)
            print(f"  cites: +{ci}")

        # ── Pass F ──
        if run_all or run_pass == "F":
            print("\n── Pass F: Detect commentary by title pattern ──")
            title_rels = await load_relation_keys(session, SOURCE_TITLE_PATTERN)
            print(f"  Existing {SOURCE_TITLE_PATTERN} relations: {len(title_rels)}")
            tc = await detect_commentary_by_title(session, text_map, title_rels)
            print(f"  commentary_on (title): +{tc}")

        # ── Pass G ──
        if run_all or run_pass == "G":
            print("\n── Pass G: Link texts to concepts by title keywords ──")
            concept_rels = await load_relation_keys(session, SOURCE_CONCEPT_MATCH)
            print(f"  Existing {SOURCE_CONCEPT_MATCH} relations: {len(concept_rels)}")
            lc = await link_texts_to_concepts(session, text_map, concept_rels)
            print(f"  associated_with (concept): +{lc}")

        # Commit or rollback
        if dry_run:
            await session.rollback()
            print("\n[DRY RUN] Changes rolled back.")
        else:
            await session.commit()
            print("\nCommitted successfully.")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured KG from buddhist_texts metadata (idempotent)."
    )
    parser.add_argument(
        "--pass", dest="run_pass", choices=["A", "B", "C", "D", "E", "F", "G"],
        help="Run only a specific pass (default: all)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show counts without committing",
    )
    args = parser.parse_args()
    asyncio.run(run(run_pass=args.run_pass, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
