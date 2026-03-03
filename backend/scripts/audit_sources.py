"""Batch HTTP accessibility audit for all active data sources.

Usage:
    cd backend
    python scripts/audit_sources.py
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

TIMEOUT = 15  # seconds per request
CONCURRENCY = 20  # max concurrent requests


async def check_url(client: httpx.AsyncClient, code: str, url: str) -> dict:
    """Check a single URL and return result dict."""
    if not url or url == "None":
        return {"code": code, "url": None, "status": "NO_URL", "detail": "no base_url configured"}

    start = time.monotonic()
    try:
        resp = await client.get(url, follow_redirects=True, timeout=TIMEOUT)
        elapsed = round(time.monotonic() - start, 2)
        return {
            "code": code,
            "url": url,
            "status": resp.status_code,
            "detail": f"{elapsed}s",
            "final_url": str(resp.url) if str(resp.url) != url else None,
        }
    except httpx.TimeoutException:
        return {"code": code, "url": url, "status": "TIMEOUT", "detail": f">{TIMEOUT}s"}
    except httpx.ConnectError as e:
        return {"code": code, "url": url, "status": "CONN_ERR", "detail": str(e)[:120]}
    except httpx.TooManyRedirects:
        return {"code": code, "url": url, "status": "REDIRECT_LOOP", "detail": "too many redirects"}
    except Exception as e:
        return {"code": code, "url": url, "status": "ERROR", "detail": f"{type(e).__name__}: {str(e)[:100]}"}


async def main():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(text(
            "SELECT code, name_zh, base_url FROM data_sources WHERE is_active = true ORDER BY code"
        ))
        sources = result.fetchall()

    await engine.dispose()

    print(f"Auditing {len(sources)} active data sources (concurrency={CONCURRENCY}, timeout={TIMEOUT}s)...\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = []

    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (compatible; FoJin-Audit/1.0)"},
        verify=False,  # some academic sites have bad certs
    ) as client:

        async def bounded_check(code, url):
            async with semaphore:
                return await check_url(client, code, url)

        tasks = [bounded_check(row[0], row[2]) for row in sources]
        results = await asyncio.gather(*tasks)

    # Categorize results
    ok = []
    problems = []

    for r in results:
        status = r["status"]
        if isinstance(status, int) and 200 <= status < 400:
            ok.append(r)
        else:
            problems.append(r)

    # Print problems
    print(f"{'='*80}")
    print(f"PROBLEMS ({len(problems)} sources)")
    print(f"{'='*80}")
    for r in sorted(problems, key=lambda x: str(x["status"])):
        print(f"  [{r['status']}] {r['code']:40s} {r['url'] or 'N/A':50s} {r['detail']}")

    print(f"\n{'='*80}")
    print(f"OK ({len(ok)} sources)")
    print(f"{'='*80}")
    for r in sorted(ok, key=lambda x: x["code"]):
        extra = f" -> {r['final_url']}" if r.get("final_url") else ""
        print(f"  [{r['status']}] {r['code']:40s} {r['detail']}{extra}")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(ok)} OK, {len(problems)} problems out of {len(sources)} total")
    print(f"{'='*80}")


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    asyncio.run(main())
