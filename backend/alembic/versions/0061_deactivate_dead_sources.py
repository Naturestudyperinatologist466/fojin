"""Deactivate sources with dead URLs.

- yunnan-lib: https://www.ynlib.cn/zy/xszl/syzp/ returns 404
- cass-religion: https://iwr.cssn.cn/ returns 403

Revision ID: 0061
Revises: 0060
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0061"
down_revision: Union[str, None] = "0060"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEAD_SOURCES = ["yunnan-lib", "cass-religion"]


def upgrade() -> None:
    conn = op.get_bind()
    for code in DEAD_SOURCES:
        conn.execute(
            sa_text("UPDATE data_sources SET is_active = FALSE WHERE code = :code"),
            {"code": code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code in DEAD_SOURCES:
        conn.execute(
            sa_text("UPDATE data_sources SET is_active = TRUE WHERE code = :code"),
            {"code": code},
        )
