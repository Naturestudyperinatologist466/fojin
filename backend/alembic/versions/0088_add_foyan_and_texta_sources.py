"""Add 佛研資訊 (FoYan) and 數字文獻學 (Texta Studio) data sources.

Two new sources:
  1. foyan — 佛研資訊: Buddhist studies resource portal aggregating classical text
     catalogs, image resources, digital scripture platforms, Tibetan canon, and
     research tools. Bilingual (zh/en).
  2. texta-studio — 數字文獻學: Digital philology platform with AI-powered tools
     for Buddhist text collation, OCR, citation matching, and NLP annotation.

Revision ID: 0088
Revises: 0087
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0088"
down_revision: Union[str, None] = "0087"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_SOURCES = [
    {
        "code": "foyan",
        "name_zh": "佛研資訊",
        "name_en": "Buddhist Studies Resources (FoYan)",
        "base_url": "https://www.foyan.online/",
        "description": (
            "佛研資訊——佛学研究数字资源导航平台，"
            "整合古籍目录、图像资源、数字佛典平台、藏文大藏经、"
            "研究工具与方法等六大板块，"
            "基于《汉文佛教文献数字化综览》(法鼓佛学学报, 2024)。"
        ),
        "access_type": "external",
        "region": "台湾",
        "languages": "lzh,bo,en",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
    {
        "code": "texta-studio",
        "name_zh": "數字文獻學",
        "name_en": "Texta Studio — Digital Philology",
        "base_url": "https://texta.studio/",
        "description": (
            "数字文献学——传统文献学的数字化延伸，"
            "提供AI校勘（维摩诘经/古籍智能对校）、碛砂藏数据库、"
            "古籍引文智能匹配、经文标注、OCR异体字识别、"
            "高僧传故事分类等九大数字人文研究工具。"
        ),
        "access_type": "external",
        "region": "台湾",
        "languages": "lzh",
        "supports_search": True,
        "supports_fulltext": True,
        "has_local_fulltext": False,
        "has_remote_fulltext": True,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    for src in NEW_SOURCES:
        conn.execute(
            sa_text("""
                INSERT INTO data_sources
                    (code, name_zh, name_en, base_url, description,
                     access_type, region, languages,
                     supports_search, supports_fulltext,
                     has_local_fulltext, has_remote_fulltext,
                     supports_iiif, supports_api, is_active)
                VALUES
                    (:code, :name_zh, :name_en, :base_url, :description,
                     :access_type, :region, :languages,
                     :supports_search, :supports_fulltext,
                     :has_local_fulltext, :has_remote_fulltext,
                     :supports_iiif, :supports_api, :is_active)
                ON CONFLICT (code) DO NOTHING
            """),
            src,
        )


def downgrade() -> None:
    conn = op.get_bind()
    for src in NEW_SOURCES:
        conn.execute(
            sa_text("DELETE FROM data_sources WHERE code = :code"),
            {"code": src["code"]},
        )
