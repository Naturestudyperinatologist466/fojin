"""Move Dunhuang sources to positions 4 and 5 within 中国大陆.

Current top positions:
  1. cbeta-cn        (-2)
  2. dianjin         (-1)
  3-7. five sources  (0)

Target:
  1. cbeta-cn        (-10)
  2. dianjin         (-9)
  3. hrfjw-dzj       (-8)  (first of the old sort=0 group)
  4. dunhuang-iiif   (-7)  敦煌遗书数据库
  5. dunhuang-academy(-6)  敦煌研究院数字敦煌
  6+. remaining      (0+)

Revision ID: 0065
Revises: 0064
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0065"
down_revision: Union[str, None] = "0064"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPDATES = [
    ("cbeta-cn", -10),
    ("dianjin", -9),
    ("hrfjw-dzj", -8),
    ("dunhuang-iiif", -7),
    ("dunhuang-academy", -6),
]

ROLLBACK = [
    ("cbeta-cn", -2),
    ("dianjin", -1),
    ("hrfjw-dzj", 0),
    ("dunhuang-iiif", 27),
    ("dunhuang-academy", 26),
]


def upgrade() -> None:
    conn = op.get_bind()
    for code, order in UPDATES:
        conn.execute(
            sa_text("UPDATE data_sources SET sort_order = :order WHERE code = :code"),
            {"code": code, "order": order},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code, order in ROLLBACK:
        conn.execute(
            sa_text("UPDATE data_sources SET sort_order = :order WHERE code = :code"),
            {"code": code, "order": order},
        )
