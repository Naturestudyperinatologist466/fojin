"""Fix canon source URLs to point to precise NLC pages.

- zhaocheng-jinzang: use NLC dedicated topic page (searchType=10021)
- yongle-beizang: use NLC digital classics search for 永乐北藏

Revision ID: 0062
Revises: 0061
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0062"
down_revision: Union[str, None] = "0061"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_URL = "http://read.nlc.cn/thematDataSearch/toGujiIndex"

UPDATES = [
    {
        "code": "zhaocheng-jinzang",
        "new_url": "http://read.nlc.cn/allSearch/searchList?searchType=10021&showType=1&pageNo=1",
    },
    {
        "code": "yongle-beizang",
        "new_url": "http://read.nlc.cn/allSearch/searchList?searchType=10024&showType=1&pageNo=1&searchWord=永乐北藏",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for u in UPDATES:
        conn.execute(
            sa_text("UPDATE data_sources SET base_url = :new_url WHERE code = :code"),
            {"code": u["code"], "new_url": u["new_url"]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for u in UPDATES:
        conn.execute(
            sa_text("UPDATE data_sources SET base_url = :old_url WHERE code = :code"),
            {"code": u["code"], "old_url": OLD_URL},
        )
