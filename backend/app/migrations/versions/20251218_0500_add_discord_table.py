"""add discord table for user integrations

Revision ID: add_discord_table
Revises: update_telegram_fields
Create Date: 2025-12-18 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT

# revision identifiers, used by Alembic.
revision = 'add_discord_table'
down_revision = 'update_telegram_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create discord table."""
    op.create_table(
        'discord',
        sa.Column('id', BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('discord_user_id', sa.String(length=32), nullable=False),
        sa.Column('guild_id', sa.String(length=32), nullable=True),
        sa.Column('channel_id', sa.String(length=32), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('global_name', sa.String(length=255), nullable=True),
        sa.Column(
            'status',
            sa.Enum('Disabled', 'Enabled', 'Active', 'Inactive', name='discordstatus', native_enum=False, length=16),
            nullable=False,
            server_default='Disabled',
            comment='Status of Discord connection: Disabled, Enabled, Active, or Inactive'
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='discord_ibfk_user', ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'discord_user_id', name='uq_discord_user_account'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create indexes
    op.create_index('idx_discord_uid', 'discord', ['discord_user_id'], unique=False)
    op.create_index('idx_discord_guild', 'discord', ['guild_id'], unique=False)


def downgrade() -> None:
    """Drop discord table."""
    op.drop_index('idx_discord_guild', table_name='discord')
    op.drop_index('idx_discord_uid', table_name='discord')
    op.drop_table('discord')
