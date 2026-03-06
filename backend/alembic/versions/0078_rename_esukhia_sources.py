"""Rename Esukhia sources to clearly distinguish Tengyur and Kangyur.

Revision ID: 0078
Revises: 0077
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0078"
down_revision: Union[str, None] = "0077"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPDATES = [
    {
        "code": "esukhia-derge",
        "name_zh": "德格版丹珠尔（论藏）— Esukhia 校对本",
        "name_en": "Derge Tengyur (Commentaries) — Esukhia Edition",
        "description": "Esukhia 德格版《丹珠尔》藏文校对文本，丹珠尔为藏文大藏经论藏部分，收录印度论师的注疏与论著，GitHub 开源，CC0 公共领域。",
    },
    {
        "code": "esukhia-kangyur",
        "name_zh": "德格版甘珠尔（经藏）— Esukhia 校对本",
        "name_en": "Derge Kangyur (Buddha's Words) — Esukhia Edition",
        "description": "Esukhia 德格版《甘珠尔》藏文校对文本，甘珠尔为藏文大藏经经藏部分，收录佛陀亲说的经律典籍，GitHub 开源，CC0 公共领域。",
    },
]

ROLLBACK = [
    {
        "code": "esukhia-derge",
        "name_zh": "Esukhia 德格丹珠尔",
        "name_en": "Esukhia Derge Tengyur",
        "description": "Esukhia 德格版《丹珠尔》藏文文本 GitHub 开源项目，经校对的 Unicode 藏文。Tier 2 资源。",
    },
    {
        "code": "esukhia-kangyur",
        "name_zh": "Esukhia 德格甘珠尔",
        "name_en": "Esukhia Derge Kangyur",
        "description": "Esukhia 德格版《甘珠尔》藏文文本 GitHub 开源项目。Tier 2 资源。",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for u in UPDATES:
        conn.execute(
            sa_text(
                "UPDATE data_sources SET name_zh = :name_zh, name_en = :name_en, "
                "description = :desc WHERE code = :code"
            ),
            {"code": u["code"], "name_zh": u["name_zh"], "name_en": u["name_en"], "desc": u["description"]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for u in ROLLBACK:
        conn.execute(
            sa_text(
                "UPDATE data_sources SET name_zh = :name_zh, name_en = :name_en, "
                "description = :desc WHERE code = :code"
            ),
            {"code": u["code"], "name_zh": u["name_zh"], "name_en": u["name_en"], "desc": u["description"]},
        )
