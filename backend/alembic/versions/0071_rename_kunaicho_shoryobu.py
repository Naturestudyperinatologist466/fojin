"""Rename Kunaicho Shoryobu source.

Revision ID: 0071
Revises: 0070
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0071"
down_revision: Union[str, None] = "0070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET name_zh = :name WHERE code = :code"),
        {"code": "kunaicho-shoryobu", "name": "日本宫内厅官方图书寮文库系统"},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text("UPDATE data_sources SET name_zh = :name WHERE code = :code"),
        {"code": "kunaicho-shoryobu", "name": "日本宫内厅书陵部汉籍集览"},
    )
