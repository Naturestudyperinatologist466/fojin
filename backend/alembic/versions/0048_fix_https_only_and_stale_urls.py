"""fix 6 HTTP-only sites (HTTPS not supported) and 2 stale redirect URLs

6 sites do not support TLS — HTTPS connections time out but HTTP works fine.
Change base_url from https:// to http://.

2 sites have moved — update base_url to the actual redirect destination.

Revision ID: 0048
Revises: 0047
Create Date: 2026-03-04
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0048"
down_revision: Union[str, None] = "0047"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (code, old_url, new_url)
FIXES = [
    # ── HTTP-only sites (no TLS) ──
    ("acmuller-dict", "https://www.acmuller.net/", "http://www.acmuller.net/"),
    ("chan-buddhism", "https://www.thezensite.com/", "http://www.thezensite.com/"),
    ("kalmyk-buddhism", "https://www.kigiran.com/", "http://www.kigiran.com/"),
    ("padmakara", "https://www.padmakara.org/", "http://www.padmakara.org/"),
    ("rkts", "https://www.rkts.org/", "http://www.rkts.org/"),
    ("pali-canon-online", "https://www.palicanon.org/", "http://www.palicanon.org/"),
    # ── Stale URLs (redirect to new location) ──
    ("dtab-bonn", "https://dtab.crossasia.org/", "https://iiif.crossasia.org/s/dtab"),
    ("jiats", "https://www.jiats.org/", "https://old.thlib.org/collections/texts/jiats/"),
]


def upgrade() -> None:
    for code, _old, new in FIXES:
        op.execute(
            f"UPDATE data_sources SET base_url = '{new}' WHERE code = '{code}'"
        )


def downgrade() -> None:
    for code, old, _new in FIXES:
        op.execute(
            f"UPDATE data_sources SET base_url = '{old}' WHERE code = '{code}'"
        )
