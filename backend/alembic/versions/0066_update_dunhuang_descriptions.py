"""Update descriptions for Dunhuang sources.

Replace generic "中国地区佛教数字资源" with specific descriptions
based on each site's actual content.

Revision ID: 0066
Revises: 0065
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0066"
down_revision: Union[str, None] = "0065"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_DESC = "中国地区佛教数字资源"

UPDATES = [
    {
        "code": "dunhuang-academy",
        "description": (
            "敦煌研究院官方数字资源平台，提供莫高窟等石窟的高清壁画影像、"
            "数字洞窟浏览、开放素材库及敦煌学研究文献库，"
            "是敦煌佛教艺术与石窟文献数字化的核心入口。"
        ),
    },
    {
        "code": "dunhuang-iiif",
        "description": (
            "国际敦煌项目(IDP)中国站，由中国国家图书馆主办，"
            "汇集英、中、法、德、俄、日、韩等国收藏的敦煌及丝绸之路写本、"
            "绘画与纺织品高清影像，支持多语种检索与目录浏览。"
        ),
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for u in UPDATES:
        conn.execute(
            sa_text(
                "UPDATE data_sources SET description = :desc WHERE code = :code"
            ),
            {"code": u["code"], "desc": u["description"]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for u in UPDATES:
        conn.execute(
            sa_text(
                "UPDATE data_sources SET description = :desc WHERE code = :code"
            ),
            {"code": u["code"], "desc": OLD_DESC},
        )
