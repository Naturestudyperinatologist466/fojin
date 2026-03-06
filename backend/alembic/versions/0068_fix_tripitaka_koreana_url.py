"""Fix Tripitaka Koreana source: update dead URL and description.

Old URL kb.nl.go.kr returns 502. Replace with Dongguk University KABC
(Korean Buddhist Canon Archive) which hosts the digitized Tripitaka
Koreana with full text and integrated translations.

Revision ID: 0068
Revises: 0067
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0068"
down_revision: Union[str, None] = "0067"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_URL = "https://kb.nl.go.kr"
OLD_DESC = "韩国国家图书馆数字化的高丽大藏经影像与元数据"

NEW_URL = "https://kabc.dongguk.edu/content/list?itemId=ABC_IT"
NEW_DESC = (
    "东国大学佛教学术院高丽大藏经数字档案(KABC)，"
    "提供通合大藏经原文与韩文翻译的全文检索与在线阅读，"
    "并收录韩国佛教全书、高丽教藏、变相图及近代佛教文献等专题资源。"
)


def upgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, description = :desc "
            "WHERE code = :code"
        ),
        {"code": "ktk", "url": NEW_URL, "desc": NEW_DESC},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, description = :desc "
            "WHERE code = :code"
        ),
        {"code": "ktk", "url": OLD_URL, "desc": OLD_DESC},
    )
