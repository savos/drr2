"""add slack table for workspace integrations

Revision ID: add_slack_table
Revises: add_year_to_cases
Create Date: 2025-12-18 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_slack_table'
down_revision = 'add_year_to_cases'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create slack table."""
    op.create_table(
        'slack',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('workspace_id', sa.CHAR(length=36), nullable=False),
        sa.Column('workspace_name', sa.String(length=128), nullable=True),
        sa.Column('bot_token', sa.Text(), nullable=False),
        sa.Column('bot_user_id', sa.String(length=32), nullable=True),
        sa.Column('slack_user_id', sa.String(length=32), nullable=True),
        sa.Column('channel_id', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='slack_ibfk_user', ondelete='CASCADE'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create indexes
    op.create_index('idx_slack_user_id', 'slack', ['user_id'], unique=False)
    op.create_index('idx_slack_workspace_id', 'slack', ['workspace_id'], unique=False)


def downgrade() -> None:
    """Drop slack table."""
    op.drop_index('idx_slack_workspace_id', table_name='slack')
    op.drop_index('idx_slack_user_id', table_name='slack')
    op.drop_table('slack')
