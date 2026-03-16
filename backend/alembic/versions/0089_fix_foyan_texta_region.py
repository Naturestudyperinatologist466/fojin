"""Fix region for foyan and texta-studio: 台湾 → 中国大陆.

Revision ID: 0089
Revises: 0088
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0089"
down_revision: Union[str, None] = "0088"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa_text("""
            UPDATE data_sources SET region = '中国大陆'
            WHERE code IN ('foyan', 'texta-studio')
        """)
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa_text("""
            UPDATE data_sources SET region = '台湾'
            WHERE code IN ('foyan', 'texta-studio')
        """)
    )
