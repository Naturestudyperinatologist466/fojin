"""Fix buddhason region: 台湾 → 中国台湾.

Unify region naming — '台湾' should be '中国台湾' to match existing convention.

Revision ID: 0090
Revises: 0089
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0090"
down_revision: Union[str, None] = "0089"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET region = '中国台湾' WHERE region = '台湾'")
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET region = '台湾' WHERE code = 'buddhason'")
    )
