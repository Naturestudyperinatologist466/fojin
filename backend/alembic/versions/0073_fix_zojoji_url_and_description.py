"""Fix Zojoji Tripitaka URL and description.

Old URL jbf.ne.jp is the Japan Buddhist Federation, not the Zojoji
digital archive. Replace with the official Sandaizo digital archive
at jodoshuzensho.jp. Update description with accurate details.

Revision ID: 0073
Revises: 0072
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0073"
down_revision: Union[str, None] = "0072"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_URL = "https://www.jbf.ne.jp/"
OLD_NAME = "增上寺元版大藏经数字档案"
OLD_DESC = "净土宗大本山增上寺所藏元版大藏经数字化项目，含宋版/元版大藏经高清影像公开"

NEW_URL = "https://jodoshuzensho.jp/zojoji_sandaizo/"
NEW_NAME = "增上寺三大藏经数字档案"
NEW_DESC = (
    "浄土宗大本山增上寺所藏三大藏经数字档案，收录思渓版大藏经（南宋）5,342帖、"
    "普宁寺版大藏经（元）5,228帖、高丽版大藏经1,357册，"
    "总计约48.4万帧高清影像，支持书名与著译者检索，2025年入选UNESCO世界记忆项目。"
)


def upgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, name_zh = :name, "
            "description = :desc WHERE code = :code"
        ),
        {"code": "zojoji-daizokyo", "url": NEW_URL, "name": NEW_NAME, "desc": NEW_DESC},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, name_zh = :name, "
            "description = :desc WHERE code = :code"
        ),
        {"code": "zojoji-daizokyo", "url": OLD_URL, "name": OLD_NAME, "desc": OLD_DESC},
    )
