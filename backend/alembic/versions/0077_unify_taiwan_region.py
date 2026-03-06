"""Unify region '台湾' to '中国台湾'.

Only 1 source uses '台湾' (DILA), the other 38 use '中国台湾'.

Revision ID: 0077
Revises: 0076
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0077"
down_revision: Union[str, None] = "0076"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET region = '中国台湾' WHERE region = '台湾'"),
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET region = '台湾' WHERE code = :code"
        ),
        {"code": "dila-authority"},
    )
