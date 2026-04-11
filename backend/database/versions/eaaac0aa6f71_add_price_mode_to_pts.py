"""add price_mode to pts

Revision ID: eaaac0aa6f71
Revises: 104ec3d074ef
Create Date: 2026-04-11 12:49:07.723520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaaac0aa6f71'
down_revision: Union[str, Sequence[str], None] = '104ec3d074ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pts",
        sa.Column("price_mode", sa.String, nullable=False, server_default="deflect"),
    )


def downgrade() -> None:
    op.drop_column("pts", "price_mode")
