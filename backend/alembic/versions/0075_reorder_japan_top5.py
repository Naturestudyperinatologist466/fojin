"""Reorder top 5 Japan sources.

1. kunaicho-shoryobu  (-5)
2. zojoji-daizokyo    (-4)
3. sat                (-3)
4. ndl-bukkyozensho   (-2)
5. icabs-koshakyo     (-1)

Revision ID: 0075
Revises: 0074
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0075"
down_revision: Union[str, None] = "0074"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPDATES = [
    ("kunaicho-shoryobu", -5),
    ("zojoji-daizokyo", -4),
    ("sat", -3),
    ("ndl-bukkyozensho", -2),
    ("icabs-koshakyo", -1),
]

ROLLBACK = [
    ("kunaicho-shoryobu", -1),
    ("zojoji-daizokyo", 0),
    ("sat", 7),
    ("ndl-bukkyozensho", 1),
    ("icabs-koshakyo", 287),
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
