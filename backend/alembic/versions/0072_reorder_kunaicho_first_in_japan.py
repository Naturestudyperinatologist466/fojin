"""Move Kunaicho Shoryobu to first position in Japan region.

Revision ID: 0072
Revises: 0071
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0072"
down_revision: Union[str, None] = "0071"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET sort_order = -1 WHERE code = :code"),
        {"code": "kunaicho-shoryobu"},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET sort_order = 95 WHERE code = :code"),
        {"code": "kunaicho-shoryobu"},
    )
