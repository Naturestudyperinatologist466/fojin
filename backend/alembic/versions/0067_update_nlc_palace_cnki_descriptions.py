"""Update descriptions for NLC, Palace Museum and CNKI sources.

Replace generic "中国地区佛教数字资源" with specific descriptions
based on each site's actual content.

Revision ID: 0067
Revises: 0066
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0067"
down_revision: Union[str, None] = "0066"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_DESC = "中国地区佛教数字资源"

UPDATES = [
    {
        "code": "nlc",
        "description": (
            "中国国家图书馆读者云门户古籍平台，含数字古籍2万余部，"
            "涵盖赵城金藏、敦煌遗珍、数字方志、碑帖菁华等20个专题库，"
            "支持免登录在线阅读与检索。"
        ),
    },
    {
        "code": "palace-museum",
        "description": (
            "故宫博物院数字文物库，以明清皇宫旧藏为基础，"
            "收录藏传佛教造像、唐卡、法器及宫廷佛教文物高清影像，"
            "支持在线浏览与专题检索。"
        ),
    },
    {
        "code": "cnki-buddhism",
        "description": (
            "中国知网学术文献平台，可检索佛学相关期刊论文、"
            "博硕士学位论文、会议论文及年鉴资料，"
            "是大陆佛教学术研究文献的主要数据库入口。"
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
