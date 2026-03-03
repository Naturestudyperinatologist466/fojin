"""
Base importer class for all data source importers.

Provides:
- DB/ES connection management
- rate_limited_get() with 429 retry
- Checkpoint-based resume (JSON file)
- ImportStats tracking
- ensure_source() auto-create DataSource
- import_logs recording
"""

import asyncio
import json
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import select, text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.source import DataSource


@dataclass
class ImportStats:
    texts_created: int = 0
    texts_updated: int = 0
    contents_created: int = 0
    identifiers_created: int = 0
    relations_created: int = 0
    errors: int = 0
    skipped: int = 0
    start_time: float = field(default_factory=time.time)

    def elapsed(self) -> float:
        return time.time() - self.start_time

    def to_dict(self) -> dict:
        return {
            "texts_created": self.texts_created,
            "texts_updated": self.texts_updated,
            "contents_created": self.contents_created,
            "identifiers_created": self.identifiers_created,
            "relations_created": self.relations_created,
            "errors": self.errors,
            "skipped": self.skipped,
            "elapsed_seconds": round(self.elapsed(), 1),
        }

    def summary(self) -> str:
        parts = []
        if self.texts_created:
            parts.append(f"texts_created={self.texts_created}")
        if self.texts_updated:
            parts.append(f"texts_updated={self.texts_updated}")
        if self.contents_created:
            parts.append(f"contents_created={self.contents_created}")
        if self.identifiers_created:
            parts.append(f"identifiers_created={self.identifiers_created}")
        if self.relations_created:
            parts.append(f"relations_created={self.relations_created}")
        if self.errors:
            parts.append(f"errors={self.errors}")
        if self.skipped:
            parts.append(f"skipped={self.skipped}")
        parts.append(f"elapsed={self.elapsed():.1f}s")
        return ", ".join(parts)


class BaseImporter(ABC):
    """Base class for all data source importers."""

    SOURCE_CODE: str = ""  # Override in subclass
    SOURCE_NAME_ZH: str = ""
    SOURCE_NAME_EN: str = ""
    SOURCE_BASE_URL: str = ""
    SOURCE_API_URL: str = ""
    SOURCE_DESCRIPTION: str = ""

    # Rate limiting
    RATE_LIMIT_DELAY: float = 1.0  # seconds between requests
    MAX_RETRIES: int = 3

    def __init__(self):
        self.stats = ImportStats()
        self.engine = None
        self.session_factory = None
        self.es: AsyncElasticsearch | None = None
        self.http: httpx.AsyncClient | None = None
        self._source: DataSource | None = None
        self._last_request_time: float = 0
        self._checkpoint_path = Path(f"data/checkpoints/{self.SOURCE_CODE}.json")

    async def setup(self):
        """Initialize DB, ES, and HTTP connections."""
        self.engine = create_async_engine(settings.database_url)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.es = AsyncElasticsearch(settings.es_host)
        self.http = httpx.AsyncClient(timeout=60.0, follow_redirects=True)

    async def teardown(self):
        """Close all connections."""
        if self.http:
            await self.http.aclose()
        if self.es:
            await self.es.close()
        if self.engine:
            await self.engine.dispose()

    async def ensure_source(self, session: AsyncSession) -> DataSource:
        """Get or create the DataSource for this importer."""
        if self._source:
            return self._source

        result = await session.execute(
            select(DataSource).where(DataSource.code == self.SOURCE_CODE)
        )
        source = result.scalar_one_or_none()

        if not source:
            source = DataSource(
                code=self.SOURCE_CODE,
                name_zh=self.SOURCE_NAME_ZH,
                name_en=self.SOURCE_NAME_EN,
                base_url=self.SOURCE_BASE_URL or None,
                api_url=self.SOURCE_API_URL or None,
                description=self.SOURCE_DESCRIPTION or None,
            )
            session.add(source)
            await session.flush()

        self._source = source
        return source

    async def rate_limited_get(self, url: str, **kwargs) -> httpx.Response:
        """Make an HTTP GET with rate limiting and 429 retry."""
        # Enforce rate limit
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)

        for attempt in range(self.MAX_RETRIES):
            try:
                self._last_request_time = time.time()
                resp = await self.http.get(url, **kwargs)

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 5))
                    print(f"  Rate limited (429). Waiting {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue

                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError:
                raise
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait = 2 ** attempt
                    print(f"  Request error: {e}. Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise

        raise RuntimeError(f"Failed after {self.MAX_RETRIES} retries: {url}")

    # Checkpoint management
    def load_checkpoint(self) -> dict:
        """Load checkpoint data for resume."""
        if self._checkpoint_path.exists():
            return json.loads(self._checkpoint_path.read_text())
        return {}

    def save_checkpoint(self, data: dict):
        """Save checkpoint data for resume."""
        self._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self._checkpoint_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def clear_checkpoint(self):
        """Remove checkpoint file after successful completion."""
        if self._checkpoint_path.exists():
            self._checkpoint_path.unlink()

    # Import log
    async def log_import_start(self, session: AsyncSession) -> int:
        """Record import start in import_logs."""
        result = await session.execute(
            text("""
                INSERT INTO import_logs (source_code, status)
                VALUES (:source_code, 'running')
                RETURNING id
            """),
            {"source_code": self.SOURCE_CODE},
        )
        await session.commit()
        return result.scalar_one()

    async def log_import_finish(
        self, session: AsyncSession, log_id: int, status: str = "success", error: str | None = None
    ):
        """Record import finish in import_logs."""
        await session.execute(
            text("""
                UPDATE import_logs
                SET status = :status,
                    finished_at = NOW(),
                    stats_json = :stats,
                    error_log = :error
                WHERE id = :id
            """),
            {
                "id": log_id,
                "status": status,
                "stats": json.dumps(self.stats.to_dict()),
                "error": error,
            },
        )
        await session.commit()

    @abstractmethod
    async def run_import(self):
        """Implement the actual import logic in subclasses."""
        ...

    async def execute(self):
        """Main entry point: setup → run → teardown with logging."""
        print(f"{'=' * 60}")
        print(f"佛津 (FoJin) — {self.SOURCE_NAME_ZH} ({self.SOURCE_CODE}) Import")
        print(f"{'=' * 60}")

        await self.setup()
        log_id = None
        try:
            async with self.session_factory() as session:
                log_id = await self.log_import_start(session)

            await self.run_import()

            async with self.session_factory() as session:
                await self.log_import_finish(session, log_id, "success")
            self.clear_checkpoint()
            print(f"\nImport complete! {self.stats.summary()}")

        except Exception as e:
            print(f"\nImport FAILED: {e}")
            if log_id:
                try:
                    async with self.session_factory() as session:
                        await self.log_import_finish(session, log_id, "failed", str(e))
                except Exception:
                    pass
            raise
        finally:
            await self.teardown()
            print(f"{'=' * 60}")
