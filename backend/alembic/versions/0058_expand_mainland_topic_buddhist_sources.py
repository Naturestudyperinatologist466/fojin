"""Expand mainland China topic-focused Buddhist text resources.

This migration continues the China-mainland audit from 2026-03-06.
It replaces several stale homepage placeholders with current official
topic pages, reactivates confirmed live mainland resources, and adds
an official museum entry for the Yunjusi stone sutra collection.

Revision ID: 0058
Revises: 0057
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0058"
down_revision: Union[str, None] = "0057"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_SOURCES = [
    {
        "code": "yunjusi-stone-museum",
        "name_zh": "云居寺石经博物馆",
        "name_en": "Yunjusi Stone Sutra Museum",
        "base_url": "https://www.bjfsh.gov.cn/ztzx/2024/fsbwg/bwgmc/202411/t20241121_40082949.shtml",
        "description": "北京市房山区官方发布的云居寺石经博物馆专题页，介绍房山石经、石经山与馆藏《乾隆大藏经》、藏汉合璧大藏经等资源，是大陆佛教石经与藏经文物的重要官方入口。",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "zh,lzh,bo",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
]

SOURCE_UPDATES = [
    {
        "code": "cass-guji",
        "name_zh": "国家哲学社会科学文献中心古籍数据库",
        "name_en": "National Center for Philosophy and Social Sciences Documentation Classical Text Database",
        "base_url": "https://www.ncpssd.cn/",
        "description": "国家哲学社会科学文献中心现行官网，提供古籍入口与经史子集检索、在线阅读及全文下载，覆盖释家类与佛教相关古籍资源。",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "zh,lzh",
        "supports_search": True,
        "supports_fulltext": True,
        "has_local_fulltext": False,
        "has_remote_fulltext": True,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
    {
        "code": "hubei-lib",
        "name_zh": "湖北历史文献资源平台",
        "name_en": "Hubei Historical Documents Platform",
        "base_url": "https://guji.library.hb.cn/",
        "description": "湖北省古籍保护中心官方平台，汇集湖北古籍普查、整理与数字资源，可在线浏览与检索湖北历史文献及相关佛教古籍线索。",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "zh,lzh",
        "supports_search": True,
        "supports_fulltext": True,
        "has_local_fulltext": False,
        "has_remote_fulltext": True,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
    {
        "code": "gansu-lib",
        "name_zh": "甘肃省图书馆西北地方文献古籍善本全文数据库",
        "name_en": "Gansu Library Full-text Database of Northwest Local Documents and Rare Books",
        "base_url": "http://dbase3.gslib.com.cn/DigitalResources/toSingleSearchView/89/XBDFWXGJSBQWSJK",
        "description": "甘肃省图书馆信息资源建设与管理平台的专题库，支持单库检索与在线阅览，内容涵盖地方史志、家谱族谱、金石碑刻、敦煌文献及西北少数民族古籍。",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "zh,lzh,bo",
        "supports_search": True,
        "supports_fulltext": True,
        "has_local_fulltext": False,
        "has_remote_fulltext": True,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
    {
        "code": "yunnan-lib",
        "name_zh": "云南省图书馆三迤珍品佛教古籍专题",
        "name_en": "Yunnan Library Buddhist Rare Books in Sanyi Treasures",
        "base_url": "https://www.ynlib.cn/zy/xszl/syzp/",
        "description": "云南省图书馆线上展览“三迤珍品”中的佛教古籍专题，收录《元官刻大藏经》《金刚般若波罗蜜经》《仁王护国般若波罗蜜多经抄》《灌顶药师经疏》等馆藏珍本。",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "zh,lzh",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": True,
    },
]

SOURCE_UPDATE_ORIGINALS = [
    {
        "code": "cass-guji",
        "name_zh": "国家哲学社会科学文献中心古籍数据库",
        "name_en": "CASS Classical Text Database",
        "base_url": "https://www.guji.cssn.cn/",
        "description": "国家哲社中心古籍影像库，19,868条记录覆盖经史子集含释家类文献，完全开放",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "lzh,zh",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": False,
    },
    {
        "code": "hubei-lib",
        "name_zh": "湖北省图书馆古籍",
        "name_en": "Hubei Provincial Library",
        "base_url": "http://www.library.hb.cn/",
        "description": "中国地区佛教数字资源",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "lzh",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": False,
    },
    {
        "code": "gansu-lib",
        "name_zh": "甘肃省图书馆敦煌文献",
        "name_en": "Gansu Library Dunhuang MSS",
        "base_url": "http://www.gslib.com.cn/",
        "description": "中国地区佛教数字资源",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "lzh",
        "supports_search": False,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": False,
    },
    {
        "code": "yunnan-lib",
        "name_zh": "云南省图书馆贝叶经",
        "name_en": "Yunnan Library Palm Leaf MSS",
        "base_url": "https://www.ynlib.cn/",
        "description": "云南省图书馆古籍数字化，9,995条记录含南传佛教贝叶经/汉传佛教典籍/少数民族文字佛经，云南佛教传统深厚覆盖南传与汉传",
        "access_type": "external",
        "region": "中国大陆",
        "languages": "lzh",
        "supports_search": True,
        "supports_fulltext": False,
        "has_local_fulltext": False,
        "has_remote_fulltext": False,
        "supports_iiif": False,
        "supports_api": False,
        "is_active": False,
    },
]


def _upsert_source(conn, source: dict) -> None:
    existing = conn.execute(
        sa_text("SELECT id FROM data_sources WHERE code = :code"),
        {"code": source["code"]},
    ).scalar()

    params = {
        "code": source["code"],
        "name_zh": source["name_zh"],
        "name_en": source["name_en"],
        "base_url": source["base_url"],
        "description": source["description"],
        "access_type": source["access_type"],
        "region": source["region"],
        "languages": source["languages"],
        "supports_search": source["supports_search"],
        "supports_fulltext": source["supports_fulltext"],
        "has_local_fulltext": source["has_local_fulltext"],
        "has_remote_fulltext": source["has_remote_fulltext"],
        "supports_iiif": source["supports_iiif"],
        "supports_api": source["supports_api"],
        "is_active": source["is_active"],
    }

    if existing:
        conn.execute(
            sa_text(
                """
                UPDATE data_sources SET
                    name_zh = :name_zh,
                    name_en = :name_en,
                    base_url = :base_url,
                    description = :description,
                    access_type = :access_type,
                    region = :region,
                    languages = :languages,
                    supports_search = :supports_search,
                    supports_fulltext = :supports_fulltext,
                    has_local_fulltext = :has_local_fulltext,
                    has_remote_fulltext = :has_remote_fulltext,
                    supports_iiif = :supports_iiif,
                    supports_api = :supports_api,
                    is_active = :is_active
                WHERE code = :code
                """
            ),
            params,
        )
        return

    conn.execute(
        sa_text(
            """
            INSERT INTO data_sources (
                code, name_zh, name_en, base_url, api_url, description,
                access_type, region, languages,
                supports_search, supports_fulltext,
                has_local_fulltext, has_remote_fulltext,
                supports_iiif, supports_api, is_active
            ) VALUES (
                :code, :name_zh, :name_en, :base_url, NULL, :description,
                :access_type, :region, :languages,
                :supports_search, :supports_fulltext,
                :has_local_fulltext, :has_remote_fulltext,
                :supports_iiif, :supports_api, :is_active
            )
            """
        ),
        params,
    )


def upgrade() -> None:
    conn = op.get_bind()
    for source in NEW_SOURCES:
        _upsert_source(conn, source)
    for source in SOURCE_UPDATES:
        _upsert_source(conn, source)


def downgrade() -> None:
    conn = op.get_bind()
    for source in SOURCE_UPDATE_ORIGINALS:
        _upsert_source(conn, source)
    for source in NEW_SOURCES:
        conn.execute(
            sa_text("DELETE FROM data_sources WHERE code = :code"),
            {"code": source["code"]},
        )
