"""Fix Kunaicho Shoryobu URL and description.

Old URL db.sido.keio.ac.jp/kanseki/ has SSL failure. Replace with the
official Imperial Household Agency Shoryobu digital catalog/image
system at shoryobu.kunaicho.go.jp.

Revision ID: 0070
Revises: 0069
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0070"
down_revision: Union[str, None] = "0069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_URL = "https://db.sido.keio.ac.jp/kanseki/"
OLD_DESC = "宫内厅书陵部所藏汉籍数字化影像，213条记录含皇室旧藏珍贵中国典籍"

NEW_URL = "https://shoryobu.kunaicho.go.jp/Toshoryo"
NEW_DESC = (
    "宫内厅书陵部所藏资料目录与画像公开系统（图书寮文库），"
    "提供皇室旧藏汉籍、古写本等数字化影像的横断检索与在线浏览，"
    "含佛教经典抄本及中国典籍珍本。"
)


def upgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, description = :desc "
            "WHERE code = :code"
        ),
        {"code": "kunaicho-shoryobu", "url": NEW_URL, "desc": NEW_DESC},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa_text(
            "UPDATE data_sources SET base_url = :url, description = :desc "
            "WHERE code = :code"
        ),
        {"code": "kunaicho-shoryobu", "url": OLD_URL, "desc": OLD_DESC},
    )
