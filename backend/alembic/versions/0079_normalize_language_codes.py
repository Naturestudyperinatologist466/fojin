"""Normalize language names to ISO codes in data_sources.languages.

Some sources store full Chinese names (古典汉文, 中文, 日语, etc.)
instead of ISO 639 codes (lzh, zh, ja, etc.). This causes the frontend
language filter dropdown to display duplicates and sort incorrectly.

Revision ID: 0079
Revises: 0078
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0079"
down_revision: Union[str, None] = "0078"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Chinese name → ISO 639 code
NAME_TO_CODE = {
    "古典汉文": "lzh",
    "中文": "zh",
    "繁体中文": "zh",
    "日语": "ja",
    "梵文": "sa",
    "藏文": "bo",
    "英语": "en",
    "德语": "de",
    "巴利文": "pi",
    "僧伽罗文": "si",
    "荷兰语": "nl",
    "高棉文": "km",
    "韩语": "ko",
    "法语": "fr",
    "西班牙语": "es",
}


def _replace_lang(languages: str) -> str:
    """Replace Chinese language names with ISO codes, dedup, preserve order."""
    parts = [l.strip() for l in languages.split(",") if l.strip()]
    result = []
    seen = set()
    for p in parts:
        code = NAME_TO_CODE.get(p, p)
        if code not in seen:
            seen.add(code)
            result.append(code)
    return ",".join(result)


# Reverse mapping for downgrade
CODE_TO_NAME = {v: k for k, v in NAME_TO_CODE.items() if k != "繁体中文"}


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa_text("SELECT id, languages FROM data_sources WHERE languages IS NOT NULL")
    ).fetchall()
    for row in rows:
        old = row[1]
        new = _replace_lang(old)
        if new != old:
            conn.execute(
                sa_text("UPDATE data_sources SET languages = :langs WHERE id = :id"),
                {"langs": new, "id": row[0]},
            )


def downgrade() -> None:
    # No-op: the ISO codes are more correct; reverting to inconsistent
    # Chinese names would cause the same frontend issues.
    pass
