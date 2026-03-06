"""Deactivate Korean Confucian Studies Network (not Buddhist).

Revision ID: 0069
Revises: 0068
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0069"
down_revision: Union[str, None] = "0068"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET is_active = FALSE WHERE code = :code"),
        {"code": "kr-confucian-net"},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET is_active = TRUE WHERE code = :code"),
        {"code": "kr-confucian-net"},
    )
