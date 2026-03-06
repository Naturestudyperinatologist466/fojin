"""Fix ctext region to US and update Brill Buddhism URL.

- ctext: region 荷兰 -> 美国 (founder at Harvard University)
- brill-buddhism: URL updated from /eob to /enbo

Revision ID: 0076
Revises: 0075
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0076"
down_revision: Union[str, None] = "0075"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa_text("UPDATE data_sources SET region = :region WHERE code = :code"),
        {"code": "ctext", "region": "美国"},
    )
    conn.execute(
        sa_text("UPDATE data_sources SET base_url = :url WHERE code = :code"),
        {"code": "brill-buddhism", "url": "https://referenceworks.brill.com/display/db/enbo"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa_text("UPDATE data_sources SET region = :region WHERE code = :code"),
        {"code": "ctext", "region": "荷兰"},
    )
    conn.execute(
        sa_text("UPDATE data_sources SET base_url = :url WHERE code = :code"),
        {"code": "brill-buddhism", "url": "https://referenceworks.brill.com/display/db/eob"},
    )
