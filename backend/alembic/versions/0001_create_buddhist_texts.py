"""create buddhist_texts table

Revision ID: 0001
Revises:
Create Date: 2026-03-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "buddhist_texts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("taisho_id", sa.String(50), nullable=True, index=True),
        sa.Column("cbeta_id", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("title_zh", sa.String(500), nullable=False, index=True),
        sa.Column("title_sa", sa.String(500), nullable=True),
        sa.Column("title_bo", sa.String(500), nullable=True),
        sa.Column("title_pi", sa.String(500), nullable=True),
        sa.Column("translator", sa.String(200), nullable=True),
        sa.Column("dynasty", sa.String(50), nullable=True),
        sa.Column("fascicle_count", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subcategory", sa.String(200), nullable=True),
        sa.Column("cbeta_url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("buddhist_texts")
