"""Deactivate 11 low-value or redundant data sources.

These sources either point to generic institutional homepages without
direct access to digital Buddhist resources, or duplicate content
already covered by other sources (e.g. CBETA, NLC).

Revision ID: 0063
Revises: 0062
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0063"
down_revision: Union[str, None] = "0062"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEACTIVATE_CODES = [
    "china-buddhist-academy",       # 中国佛学院
    "china-tibetan-buddhist-academy",  # 中国藏语系高级佛学院
    "renmin-buddhism",              # 中国人民大学佛教与宗教学理论研究所
    "yunjusi-stone-museum",         # 云居寺石经博物馆
    "jiangsu-guji",                 # 江苏省古籍数字资源集成平台
    "zhaocheng-jinzang",            # 赵城金藏
    "yongle-beizang",               # 永乐北藏
    "fangshan-stone",               # 房山石经数据库
    "jiaxing-zang",                 # 嘉兴藏数字化项目
    "hubei-lib",                    # 湖北历史文献资源平台
    "cter",                         # 汉文佛教大藏经电子资源(CTER)
]


def upgrade() -> None:
    conn = op.get_bind()
    for code in DEACTIVATE_CODES:
        conn.execute(
            sa_text("UPDATE data_sources SET is_active = FALSE WHERE code = :code"),
            {"code": code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code in DEACTIVATE_CODES:
        conn.execute(
            sa_text("UPDATE data_sources SET is_active = TRUE WHERE code = :code"),
            {"code": code},
        )
