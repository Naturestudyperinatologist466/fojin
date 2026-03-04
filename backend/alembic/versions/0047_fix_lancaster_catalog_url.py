"""fix lancaster-catalog base_url: HTTPS → HTTP (site does not support TLS)

Revision ID: 0047
Revises: 0046
Create Date: 2026-03-04
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0047"
down_revision: Union[str, None] = "0046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE data_sources SET base_url = 'http://www.acmuller.net/descriptive_catalogue/' "
        "WHERE code = 'lancaster-catalog'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE data_sources SET base_url = 'https://www.acmuller.net/descriptive_catalogue/' "
        "WHERE code = 'lancaster-catalog'"
    )
