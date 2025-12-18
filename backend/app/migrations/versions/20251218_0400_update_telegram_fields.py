"""update telegram table - add deleted_at and rename chat_id to channel_id

Revision ID: update_telegram_fields
Revises: add_telegram_table
Create Date: 2025-12-18 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_telegram_fields'
down_revision = 'add_telegram_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename chat_id to channel_id (deleted_at already exists)."""
    # Use raw SQL to rename the column - MySQL will automatically update the unique constraint
    op.execute("ALTER TABLE telegram CHANGE COLUMN chat_id channel_id BIGINT NOT NULL")

    # Create the index on channel_id
    op.create_index('idx_telegram_channel', 'telegram', ['channel_id'], unique=False)


def downgrade() -> None:
    """Rename channel_id back to chat_id."""
    # Drop the index on channel_id
    op.drop_index('idx_telegram_channel', table_name='telegram')

    # Use raw SQL to rename the column back
    op.execute("ALTER TABLE telegram CHANGE COLUMN channel_id chat_id BIGINT NOT NULL")
