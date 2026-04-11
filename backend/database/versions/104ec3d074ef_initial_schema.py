"""initial schema

Revision ID: 104ec3d074ef
Revises:
Create Date: 2026-04-11 07:27:24.722738

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "104ec3d074ef"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("clerk_user_id", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("instagram_account_id", sa.String),
        sa.Column("instagram_token", sa.String),
        sa.Column("slug", sa.String, nullable=False),
        sa.Column("tone_config", sa.Text),
        sa.Column("calendly_link", sa.String),
        sa.Column("onboarding_complete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("stripe_customer_id", sa.String),
        sa.Column("subscription_status", sa.String),
        sa.Column("plan", sa.String),
        sa.Column("trial_ends_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("clerk_user_id", name="uq_pts_clerk_user_id"),
        sa.UniqueConstraint("instagram_account_id", name="uq_pts_instagram_account_id"),
        sa.UniqueConstraint("slug", name="uq_pts_slug"),
    )

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("pt_id", sa.Integer, sa.ForeignKey("pts.id"), nullable=False),
        sa.Column("sender_id", sa.String, nullable=False),
        sa.Column("channel", sa.String, nullable=False, server_default="instagram"),
        sa.Column("status", sa.String, nullable=False, server_default="in_progress"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("pt_id", "sender_id", name="uq_contact_pt_sender"),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contact_id", sa.Integer, sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("contacts")
    op.drop_table("pts")
