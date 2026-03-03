"""
Print global data coverage statistics (by source × language).

Usage:
    python scripts/import_stats.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.source import DataSource, TextIdentifier
from app.models.text import BuddhistText, TextContent


LANG_NAMES = {
    "lzh": "古汉",
    "zh": "中文",
    "sa": "梵文",
    "pi": "巴利",
    "bo": "藏文",
    "en": "英文",
    "pgd": "犍陀罗",
    "ko": "韩文",
    "ja": "日文",
    "my": "缅文",
}


async def main():
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        print("=" * 80)
        print("佛津 (FoJin) — 数据覆盖率统计")
        print("=" * 80)

        # Overall counts
        total_texts = (await session.execute(
            select(func.count(BuddhistText.id))
        )).scalar() or 0
        total_contents = (await session.execute(
            select(func.count(TextContent.id))
        )).scalar() or 0
        total_chars = (await session.execute(
            select(func.coalesce(func.sum(TextContent.char_count), 0))
        )).scalar() or 0

        print(f"\n总计: {total_texts:,} 部经典 | {total_contents:,} 卷内容 | {total_chars:,} 字符")

        # By source
        print(f"\n{'─' * 80}")
        print(f"{'数据源':<20} {'代码':<15} {'文本数':>10} {'内容数':>10} {'字符数':>15}")
        print(f"{'─' * 80}")

        sources = (await session.execute(
            select(DataSource).order_by(DataSource.id)
        )).scalars().all()

        # Also count texts without explicit source
        no_source_count = (await session.execute(
            select(func.count(BuddhistText.id)).where(BuddhistText.source_id.is_(None))
        )).scalar() or 0

        if no_source_count > 0:
            no_source_contents = (await session.execute(
                select(func.count(TextContent.id))
                .join(BuddhistText, TextContent.text_id == BuddhistText.id)
                .where(BuddhistText.source_id.is_(None))
            )).scalar() or 0
            no_source_chars = (await session.execute(
                select(func.coalesce(func.sum(TextContent.char_count), 0))
                .join(BuddhistText, TextContent.text_id == BuddhistText.id)
                .where(BuddhistText.source_id.is_(None))
            )).scalar() or 0
            print(f"{'(无来源/CBETA)':<20} {'cbeta':<15} {no_source_count:>10,} {no_source_contents:>10,} {no_source_chars:>15,}")

        for src in sources:
            text_count = (await session.execute(
                select(func.count(BuddhistText.id)).where(BuddhistText.source_id == src.id)
            )).scalar() or 0

            content_count = (await session.execute(
                select(func.count(TextContent.id))
                .join(BuddhistText, TextContent.text_id == BuddhistText.id)
                .where(BuddhistText.source_id == src.id)
            )).scalar() or 0

            char_count = (await session.execute(
                select(func.coalesce(func.sum(TextContent.char_count), 0))
                .join(BuddhistText, TextContent.text_id == BuddhistText.id)
                .where(BuddhistText.source_id == src.id)
            )).scalar() or 0

            name = src.name_zh[:18] if src.name_zh else src.code
            print(f"{name:<20} {src.code:<15} {text_count:>10,} {content_count:>10,} {char_count:>15,}")

        # By language
        print(f"\n{'─' * 60}")
        print(f"{'语言':<20} {'代码':<10} {'文本数':>10} {'内容数':>10}")
        print(f"{'─' * 60}")

        lang_stats = (await session.execute(
            select(
                BuddhistText.lang,
                func.count(BuddhistText.id),
            ).group_by(BuddhistText.lang)
        )).all()

        for lang_code, count in sorted(lang_stats, key=lambda x: -x[1]):
            lang_name = LANG_NAMES.get(lang_code, lang_code)

            content_count = (await session.execute(
                select(func.count(TextContent.id))
                .join(BuddhistText, TextContent.text_id == BuddhistText.id)
                .where(BuddhistText.lang == lang_code)
            )).scalar() or 0

            print(f"{lang_name:<20} {lang_code:<10} {count:>10,} {content_count:>10,}")

        # Recent import logs
        print(f"\n{'─' * 80}")
        print("最近导入记录:")
        print(f"{'─' * 80}")

        try:
            logs = (await session.execute(
                text("""
                    SELECT source_code, status, started_at, finished_at, stats_json
                    FROM import_logs
                    ORDER BY started_at DESC
                    LIMIT 10
                """)
            )).all()

            if logs:
                print(f"{'来源':<15} {'状态':<10} {'开始时间':<22} {'耗时':>10}")
                for log in logs:
                    source_code, status, started, finished, stats = log
                    elapsed = ""
                    if finished and started:
                        delta = finished - started
                        elapsed = f"{delta.total_seconds():.1f}s"
                    print(f"{source_code:<15} {status:<10} {str(started)[:19]:<22} {elapsed:>10}")
            else:
                print("  暂无导入记录")
        except Exception:
            print("  (import_logs 表不存在，请先运行迁移)")

        print(f"\n{'=' * 80}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
