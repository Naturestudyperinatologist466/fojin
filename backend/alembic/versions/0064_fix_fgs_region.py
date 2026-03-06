"""Fix Fo Guang Shan region from 中国 to 中国台湾.

Revision ID: 0064
Revises: 0063
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0064"
down_revision: Union[str, None] = "0063"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET region = :new WHERE code = :code"),
        {"code": "fgs-lib", "new": "中国台湾"},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET region = :old WHERE code = :code"),
        {"code": "fgs-lib", "old": "中国"},
    )
