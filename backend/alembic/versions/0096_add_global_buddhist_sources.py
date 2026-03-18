"""add 30 global Buddhist digital text sources

Covers South/Southeast Asia, East Asia, Europe, Americas, and
Tibetan/Central Asian Buddhist digital heritage resources.

Revision ID: 0096
Revises: 0095
Create Date: 2026-03-18
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0096"
down_revision: str | None = "0095"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCES = [
    # ── South & Southeast Asia ──
    {
        "code": "mahidol-budsir",
        "name_zh": "玛希隆大学巴利三藏检索系统",
        "name_en": "Mahidol University BUDSIR",
        "base_url": "https://www.mahidol.ac.th/budsir/",
        "description": "泰国玛希隆大学开发的巴利三藏及注释书全文检索系统，含45卷巴利三藏和70卷注释书",
        "region": "泰国", "languages": "pi,th", "access_type": "restricted",
    },
    {
        "code": "efeo-lanna-manuscripts",
        "name_zh": "法国远东学院兰纳写本数据库",
        "name_en": "EFEO Lanna Manuscripts Database",
        "base_url": "https://lanna-manuscripts.efeo.fr/",
        "description": "法国远东学院数字化的泰国北部兰纳地区佛教写本，收录来自41座寺院图书馆的18000余页写本",
        "region": "泰国", "languages": "pi,th", "access_type": "open",
    },
    {
        "code": "crossasia-lanna",
        "name_zh": "柏林跨亚洲兰纳写本数字馆",
        "name_en": "CrossAsia Northern Thai Manuscripts",
        "base_url": "https://digital.crossasia.org/digital-library-of-northern-thai-manuscripts/",
        "description": "柏林国家图书馆与宾大、清迈大学合作建设的兰纳写本数字馆藏，收录6000余件泰北写本",
        "region": "泰国", "languages": "pi,th,my", "access_type": "open",
    },
    {
        "code": "mmdl-toronto",
        "name_zh": "缅甸写本数字图书馆",
        "name_en": "Myanmar Manuscript Digital Library",
        "base_url": "https://myanmarmanuscripts.org/",
        "description": "多伦多大学主持的缅甸巴利文佛教写本开放获取数字档案，含约1000件写本",
        "region": "缅甸", "languages": "pi,my", "access_type": "open",
    },
    {
        "code": "tipitakapali-org",
        "name_zh": "巴利三藏在线阅读平台",
        "name_en": "TipitakaPali.org",
        "base_url": "https://tipitakapali.org/",
        "description": "基于VRI第六次结集三藏的在线阅读平台，支持多种文字显示并内置巴利词典即时查词",
        "region": "印度", "languages": "pi", "access_type": "open",
    },
    {
        "code": "pitaka-lk",
        "name_zh": "斯里兰卡僧伽罗语三藏数字图书馆",
        "name_en": "Pitaka.lk",
        "base_url": "https://pitaka.lk/",
        "description": "斯里兰卡三藏数字馆，提供佛陀胜利版巴利-僧伽罗语对照三藏及数百种佛学著作的在线阅读",
        "region": "斯里兰卡", "languages": "si,pi", "access_type": "open",
    },
    {
        "code": "cik-khmer-inscriptions",
        "name_zh": "高棉铭文总集",
        "name_en": "Corpus des Inscriptions Khmeres",
        "base_url": "https://cik.efeo.fr/",
        "description": "法国远东学院维护的高棉铭文数据库，收录从5世纪至14世纪的1562条铭文编目及拓片数字化",
        "region": "柬埔寨", "languages": "sa,km", "access_type": "open",
    },
    {
        "code": "chakma-digital-library",
        "name_zh": "查克玛数字图书馆",
        "name_en": "Chakma Digital Library",
        "base_url": "https://chakmalibrary.net/",
        "description": "孟加拉国查克玛族佛教文献数字化平台，收录查克玛语、孟加拉语及英语的上座部佛教典籍",
        "region": "孟加拉国", "languages": "bn,en,pi", "access_type": "open",
    },
    # ── East Asia ──
    {
        "code": "ryukoku-darc",
        "name_zh": "龙谷大学DARC贵重资料影像数据库",
        "name_en": "Ryukoku University DARC Rare Document Database",
        "base_url": "https://darc.ryukoku.ac.jp/",
        "description": "龙谷大学数字档案研究中心，含2873种、5764卷、247026件数字化善本及19000余件中亚出土文献",
        "region": "日本", "languages": "lzh,ja,sa,bo", "access_type": "open",
    },
    {
        "code": "toji-hyakugo",
        "name_zh": "东寺百合文书数字档案",
        "name_en": "Toji Hyakugo Monjo Digital Archive",
        "base_url": "https://hyakugo.pref.kyoto.lg.jp/",
        "description": "联合国教科文组织世界记忆遗产——东寺百合文书全文数字化，含近25000件中世日本佛教寺院文书",
        "region": "日本", "languages": "ja,lzh", "access_type": "open",
    },
    {
        "code": "koyasan-digital-museum",
        "name_zh": "高野山数字博物馆",
        "name_en": "Koyasan Digital Museum",
        "base_url": "https://www.dmckoyasan.com/en/digitalmuseum/",
        "description": "高野山密教文化遗产数字展示平台，提供真言宗密教相关文物、曼荼罗绘画及空海相关史料",
        "region": "日本", "languages": "ja,en", "access_type": "open",
    },
    {
        "code": "dongguk-hangul-tripitaka",
        "name_zh": "东国大学韩文大藏经全文数据库",
        "name_en": "Dongguk University Hangul Tripitaka Database",
        "base_url": "https://www.tripitaka.or.kr/",
        "description": "东国大学佛教学术院运营的韩文大藏经在线全文检索，以高丽大藏经为底本提供现代韩语翻译",
        "region": "韩国", "languages": "ko,lzh", "access_type": "open",
    },
    {
        "code": "bdrc-nlm",
        "name_zh": "BDRC蒙古国家图书馆藏经数字化",
        "name_en": "BDRC National Library of Mongolia Collection",
        "base_url": "https://library.bdrc.io/show/bdr:PR1NLM00",
        "description": "BDRC与亚洲遗产图书馆合作数字化蒙古国家图书馆31000余卷藏文写本及木刻本，1437818页扫描",
        "region": "蒙古", "languages": "bo,mn", "access_type": "open",
    },
    {
        "code": "komazawa-zenpon",
        "name_zh": "驹泽大学禅籍善本图录",
        "name_en": "Komazawa University Zen Rare Manuscript Catalogue",
        "base_url": "https://www.komazawa-u.ac.jp/facilities/library/collection/",
        "description": "驹泽大学图书馆数字化的202种禅宗珍稀写本及古刊本高清影像，日本最重要的禅宗善本数字化项目",
        "region": "日本", "languages": "lzh,ja", "access_type": "open",
    },
    # ── Europe ──
    {
        "code": "buddhistroad-bochum",
        "name_zh": "佛教之路开放获取出版",
        "name_en": "BuddhistRoad Open Access Publications",
        "base_url": "https://omp.ub.rub.de/index.php/BuddhistRoad/catalog",
        "description": "ERC资助的中亚佛教传播研究项目出版平台，收录38篇丝路沿线佛教传统一手文献研究",
        "region": "德国", "languages": "en,de", "access_type": "open",
    },
    {
        "code": "intellexus-hamburg",
        "name_zh": "Intellexus印藏佛教文本语料库映射平台",
        "name_en": "Intellexus – Mapping Indic and Tibetic Buddhist Corpora",
        "base_url": "https://intellexus.net/",
        "description": "汉堡大学ERC资助项目，运用计算工具分析梵文与藏文佛教三大文本语料库的构成史与概念谱系",
        "region": "德国", "languages": "en,sa,bo", "access_type": "restricted",
    },
    {
        "code": "leiden-asian-digital",
        "name_zh": "莱顿大学数字馆藏亚洲写本",
        "name_en": "Leiden University Digital Collections – Asian Manuscripts",
        "base_url": "https://digitalcollections.universiteitleiden.nl/",
        "description": "莱顿大学数字化平台，含范马南藏文佛教木刻本998件、手写本576件及300余件梵文贝叶经",
        "region": "荷兰", "languages": "en,bo,sa", "access_type": "open",
    },
    {
        "code": "soas-digital",
        "name_zh": "伦敦大学亚非学院数字馆藏",
        "name_en": "SOAS Digital Collections",
        "base_url": "https://digital.soas.ac.uk/",
        "description": "伦敦大学亚非学院数字化平台，含藏文木刻本、僧伽罗文与巴利文贝叶经、敦煌写本等多语种佛教文献",
        "region": "英国", "languages": "en,bo,pi,si,lzh", "access_type": "open",
    },
    {
        "code": "nlr-oriental-mss",
        "name_zh": "俄罗斯国家图书馆东方写本部",
        "name_en": "National Library of Russia – Oriental Manuscripts",
        "base_url": "https://nlr.ru/eng/RA2688/oriental-manuscripts",
        "description": "圣彼得堡俄罗斯国家图书馆东方写本部，藏有28000件东方文献含梵文贝叶经、藏文写本及敦煌佛教写本",
        "region": "俄罗斯", "languages": "en,ru,sa,bo,lzh", "access_type": "restricted",
    },
    {
        "code": "manuscriptorium-nkp",
        "name_zh": "欧洲写本文化遗产数字图书馆",
        "name_en": "Manuscriptorium",
        "base_url": "https://www.manuscriptorium.com/",
        "description": "捷克国家图书馆主导的泛欧写本数字图书馆，聚合约20国180余家机构36万条写本著录含东方贝叶经",
        "region": "捷克", "languages": "en,cs,de", "access_type": "open",
    },
    # ── Americas & Oceania ──
    {
        "code": "lywa",
        "name_zh": "耶喜喇嘛智慧档案馆",
        "name_en": "Lama Yeshe Wisdom Archive",
        "base_url": "https://www.lamayeshe.com/",
        "description": "耶喜喇嘛和梭巴仁波切的教法数字档案，含18000+小时音频与16000篇开示文稿，免费开放",
        "region": "美国", "languages": "en,bo", "access_type": "open",
    },
    {
        "code": "tsadra-buddhanature",
        "name_zh": "Tsadra佛性专题资源库",
        "name_en": "Tsadra Buddha-Nature Resource",
        "base_url": "https://buddhanature.tsadra.org/",
        "description": "Tsadra基金会如来藏（佛性）专题多媒体资源平台，汇集经典、论著、传承谱系与学术研究",
        "region": "美国", "languages": "en,bo,sa", "access_type": "open",
    },
    {
        "code": "thl-uva",
        "name_zh": "藏喜马拉雅图书馆",
        "name_en": "Tibetan & Himalayan Library (UVA)",
        "base_url": "https://thlib.org/",
        "description": "弗吉尼亚大学藏喜马拉雅数字图书馆，涵盖宁玛旧译密续全集、甘珠尔/丹珠尔目录及地理文化资源",
        "region": "美国", "languages": "en,bo", "access_type": "open",
    },
    {
        "code": "trungpa-digital",
        "name_zh": "创巴仁波切数字图书馆",
        "name_en": "Chogyam Trungpa Digital Library",
        "base_url": "https://library.chogyamtrungpa.com/",
        "description": "创巴仁波切1970-1986年500+场公开教学的音视频与可搜索文字稿数字档案",
        "region": "美国", "languages": "en", "access_type": "open",
    },
    {
        "code": "khyentse-vision",
        "name_zh": "钦哲愿景翻译计划",
        "name_en": "Khyentse Vision Project",
        "base_url": "https://www.khyentsevision.org/",
        "description": "钦哲基金会旗下翻译项目，致力于将蒋扬钦哲旺波全集译为英文并数字化开放",
        "region": "美国", "languages": "bo,en", "access_type": "open",
    },
    {
        "code": "mangalam-btw",
        "name_zh": "Mangalam佛教翻译工作台",
        "name_en": "Buddhist Translators Workbench",
        "base_url": "https://btw.mangalamresearch.org/",
        "description": "Mangalam研究中心开发的佛教翻译辅助工具，含梵文佛教术语可视化词典与同义词库",
        "region": "美国", "languages": "sa,en", "access_type": "open",
    },
    {
        "code": "yale-beinecke-buddhist",
        "name_zh": "耶鲁大学拜内克图书馆佛教写本",
        "name_en": "Yale Beinecke Buddhist Manuscripts",
        "base_url": "https://collections.library.yale.edu/",
        "description": "耶鲁大学拜内克善本图书馆藏斯里兰卡贝叶写本、尼泊尔梵文写本及韩国佛教善本数字化馆藏",
        "region": "美国", "languages": "sa,si,ko,en", "access_type": "open",
    },
    {
        "code": "anu-xu-dishan",
        "name_zh": "澳大利亚国立大学许地山文库",
        "name_en": "ANU Xu Dishan Collection",
        "base_url": "https://library-admin.anu.edu.au/collections/xu-dishan-collection/",
        "description": "澳大利亚国立大学许地山文库数字化项目，含469种1224册佛教、道教珍稀典籍全部数字化免费开放",
        "region": "澳大利亚", "languages": "lzh,zh", "access_type": "open",
    },
    # ── Tibetan & Central Asian ──
    {
        "code": "eap-menri-bon",
        "name_zh": "曼日寺苯教写本",
        "name_en": "EAP Menri Monastery Bon Manuscripts",
        "base_url": "https://eap.bl.uk/project/EAP687",
        "description": "大英图书馆濒危档案项目数字化印度曼日寺苯教写本62854页及479张手绘灌顶卡，世界最大苯教文献集",
        "region": "印度", "languages": "bo", "access_type": "open",
    },
    {
        "code": "eap-dambadarjaa",
        "name_zh": "达姆巴达尔扎寺写本",
        "name_en": "EAP Dambadarjaa Monastery Manuscripts",
        "base_url": "https://eap.bl.uk/project/EAP529",
        "description": "大英图书馆濒危档案项目数字化蒙古达姆巴达尔扎寺19-20世纪初佛教写本，涵盖蒙文与藏文文献",
        "region": "蒙古", "languages": "mn,bo", "access_type": "open",
    },
    {
        "code": "vhmml",
        "name_zh": "HMML佛教写本阅览室",
        "name_en": "HMML Virtual Reading Room",
        "base_url": "https://www.vhmml.org/readingRoom/",
        "description": "希尔博物馆写本图书馆虚拟阅览室，含尼泊尔、老挝等地佛教印度教梵文贝叶经写本数字影像48.6万件",
        "region": "美国", "languages": "sa,ne,pi,lo", "access_type": "restricted",
    },
]


def _q(s: str) -> str:
    return s.replace("'", "''") if s else ""


def upgrade() -> None:
    for s in SOURCES:
        code = _q(s["code"])
        name_zh = _q(s["name_zh"])
        name_en = _q(s["name_en"])
        base_url = _q(s["base_url"])
        desc = _q(s["description"])
        region = _q(s["region"])
        langs = _q(s["languages"])
        access = _q(s["access_type"])
        op.execute(
            sa_text(f"""
                INSERT INTO data_sources
                    (code, name_zh, name_en, base_url, description,
                     access_type, region, languages, is_active)
                VALUES
                    ('{code}', '{name_zh}', '{name_en}', '{base_url}', '{desc}',
                     '{access}', '{region}', '{langs}', true)
                ON CONFLICT (code) DO NOTHING
            """)
        )


def downgrade() -> None:
    codes = ", ".join(f"'{_q(s['code'])}'" for s in SOURCES)
    op.execute(sa_text(f"DELETE FROM data_sources WHERE code IN ({codes})"))
