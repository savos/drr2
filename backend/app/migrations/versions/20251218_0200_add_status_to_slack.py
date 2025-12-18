"""add status field to slack table

Revision ID: add_status_to_slack
Revises: add_slack_table
Create Date: 2025-12-18 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_status_to_slack'
down_revision = 'add_slack_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add status column to slack table."""
    # Add status column with default value
    op.add_column(
        'slack',
        sa.Column(
            'status',
            sa.Enum('Disabled', 'Enabled', 'Active', name='slackstatus', native_enum=False, length=20),
            nullable=False,
            server_default='Disabled',
            comment='Status of Slack integration: Disabled, Enabled, or Active'
        )
    )


def downgrade() -> None:
    """Remove status column from slack table."""
    op.drop_column('slack', 'status')
