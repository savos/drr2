"""add telegram table for DM connections

Revision ID: add_telegram_table
Revises: add_status_to_slack
Create Date: 2025-12-18 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT

# revision identifiers, used by Alembic.
revision = 'add_telegram_table'
down_revision = 'add_status_to_slack'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create telegram table."""
    op.create_table(
        'telegram',
        sa.Column('id', BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=True),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=16), nullable=True),
        sa.Column(
            'status',
            sa.Enum('Disabled', 'Enabled', 'Active', 'Inactive', name='telegramstatus', native_enum=False, length=16),
            nullable=False,
            server_default='Disabled',
            comment='Status of Telegram connection: Disabled, Enabled, Active, or Inactive'
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='telegram_ibfk_user', ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'chat_id', name='uq_telegram_user_chat'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create indexes
    op.create_index('idx_telegram_chat', 'telegram', ['chat_id'], unique=False)
    op.create_index('idx_telegram_uid', 'telegram', ['telegram_user_id'], unique=False)


def downgrade() -> None:
    """Drop telegram table."""
    op.drop_index('idx_telegram_uid', table_name='telegram')
    op.drop_index('idx_telegram_chat', table_name='telegram')
    op.drop_table('telegram')
