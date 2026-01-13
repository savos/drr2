"""Add owned_guild_ids column to discord table for tracking user-owned servers

Revision ID: 0005_discord_owned_guilds
Revises: 0004_adjust_uniques
Create Date: 2026-01-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0005_discord_owned_guilds'
down_revision = '0004_adjust_uniques'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'discord',
        sa.Column('owned_guild_ids', sa.String(length=2000), nullable=True, comment='Comma-separated list of guild IDs user owns')
    )


def downgrade() -> None:
    op.drop_column('discord', 'owned_guild_ids')
