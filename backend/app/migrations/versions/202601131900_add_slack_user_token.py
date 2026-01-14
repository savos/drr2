"""Add Slack user token column for listing user-created channels

Revision ID: 0007_slack_user_token
Revises: 0006_password_reset
Create Date: 2026-01-13 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0007_slack_user_token"
down_revision = "0006_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "slack",
        sa.Column(
            "user_token",
            sa.Text(),
            nullable=True,
            comment="Slack user access token for listing user-created channels",
        ),
    )


def downgrade() -> None:
    op.drop_column("slack", "user_token")
