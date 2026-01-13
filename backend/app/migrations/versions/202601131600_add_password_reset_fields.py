"""Add password reset token fields to users table

Revision ID: 0006_password_reset
Revises: 0005_discord_owned_guilds
Create Date: 2026-01-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0006_password_reset'
down_revision = '0005_discord_owned_guilds'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('reset_token', sa.String(length=256), nullable=True)
    )
    op.add_column(
        'users',
        sa.Column('reset_token_expires', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
