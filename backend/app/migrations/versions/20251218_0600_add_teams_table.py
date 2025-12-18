"""add teams table for DM connections

Revision ID: add_teams_table
Revises: add_discord_table
Create Date: 2025-12-18 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, JSON

# revision identifiers, used by Alembic.
revision = 'add_teams_table'
down_revision = 'add_discord_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create teams table."""
    op.create_table(
        'teams',
        sa.Column('id', BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('service_url', sa.String(length=512), nullable=False),
        sa.Column('conversation_id', sa.String(length=255), nullable=False),
        sa.Column('teams_user_id', sa.String(length=255), nullable=False),
        sa.Column('conversation_ref_json', JSON, nullable=False),
        sa.Column(
            'status',
            sa.Enum('Disabled', 'Enabled', 'Active', 'Inactive', name='teamsstatus', native_enum=False, length=16),
            nullable=False,
            server_default='Disabled',
            comment='Status of Teams connection: Disabled, Enabled, Active, or Inactive'
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='teams_ibfk_user', ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'tenant_id', 'teams_user_id', name='uq_teams_user_tenant'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create indexes
    op.create_index('idx_teams_tenant', 'teams', ['tenant_id'], unique=False)
    op.create_index('idx_teams_user_id', 'teams', ['teams_user_id'], unique=False)


def downgrade() -> None:
    """Drop teams table."""
    op.drop_index('idx_teams_user_id', table_name='teams')
    op.drop_index('idx_teams_tenant', table_name='teams')
    op.drop_table('teams')
