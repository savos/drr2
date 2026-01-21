"""Make hashed_password nullable for users added by superuser

Revision ID: 0007_password_nullable
Revises: 0006_password_reset
Create Date: 2026-01-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0008_password_nullable'
down_revision = '0007_slack_user_token'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=1024),
        nullable=True
    )


def downgrade() -> None:
    # Note: This will fail if there are users with NULL passwords
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=1024),
        nullable=False
    )
