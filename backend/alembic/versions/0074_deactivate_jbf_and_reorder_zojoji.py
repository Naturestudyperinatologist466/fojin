"""Deactivate JBF source and move Zojoji to 2nd in Japan.

- Deactivate any source pointing to jbf.ne.jp (if exists separately)
- Set zojoji-daizokyo sort_order to 2nd position in Japan region

Revision ID: 0074
Revises: 0073
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "0074"
down_revision: Union[str, None] = "0073"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # Deactivate any source with jbf.ne.jp URL
    conn.execute(
        sa_text(
            "UPDATE data_sources SET is_active = FALSE "
            "WHERE base_url LIKE :url"
        ),
        {"url": "%jbf.ne.jp%"},
    )
    # kunaicho-shoryobu is -1, set zojoji to 0 (before the old sort=0 group)
    # But old sort=0 group exists — need to check. Current Japan #1 is -1.
    # Set zojoji to -0.5? No, integer. Set to 0 but zojoji id < others?
    # Safer: shift all Japan sources with sort_order >= 0 up by 1,
    # then set zojoji to 0.
    conn.execute(
        sa_text(
            "UPDATE data_sources SET sort_order = sort_order + 1 "
            "WHERE region = :region AND sort_order >= 0 AND code != :code"
        ),
        {"region": "日本", "code": "zojoji-daizokyo"},
    )
    conn.execute(
        sa_text("UPDATE data_sources SET sort_order = 0 WHERE code = :code"),
        {"code": "zojoji-daizokyo"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa_text(
            "UPDATE data_sources SET is_active = TRUE "
            "WHERE base_url LIKE :url"
        ),
        {"url": "%jbf.ne.jp%"},
    )
    conn.execute(
        sa_text("UPDATE data_sources SET sort_order = 381 WHERE code = :code"),
        {"code": "zojoji-daizokyo"},
    )
    conn.execute(
        sa_text(
            "UPDATE data_sources SET sort_order = sort_order - 1 "
            "WHERE region = :region AND sort_order >= 1 AND code != :code"
        ),
        {"region": "日本", "code": "zojoji-daizokyo"},
    )
