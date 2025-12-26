"""update_teams_for_oauth_multi_channel

Revision ID: fb3bd8fa22b5
Revises: 1d3966e77f4b
Create Date: 2025-12-26 16:01:55.940262

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fb3bd8fa22b5'
down_revision = '1d3966e77f4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update Teams table for OAuth and multi-channel support
    op.add_column('teams', sa.Column('email', sa.String(length=255), nullable=True, comment="User's email address"))
    op.add_column('teams', sa.Column('username', sa.String(length=255), nullable=True, comment="User's display name"))
    op.add_column('teams', sa.Column('team_id', sa.String(length=255), nullable=True, comment='Teams team ID - NULL for DMs'))
    op.add_column('teams', sa.Column('team_name', sa.String(length=255), nullable=True, comment='Teams team name - NULL for DMs'))
    op.add_column('teams', sa.Column('channel_id', sa.String(length=255), nullable=True, comment='Teams channel ID - NULL for DMs'))
    op.add_column('teams', sa.Column('channel_name', sa.String(length=255), nullable=True, comment='Teams channel name - NULL for DMs'))
    op.add_column('teams', sa.Column('access_token', sa.Text(), nullable=True, comment='Encrypted OAuth access token'))
    op.add_column('teams', sa.Column('refresh_token', sa.Text(), nullable=True, comment='Encrypted OAuth refresh token'))
    op.add_column('teams', sa.Column('token_expires_at', sa.DateTime(), nullable=True, comment='Access token expiration timestamp'))
    op.alter_column('teams', 'teams_user_id',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               comment='Microsoft Teams user ID',
               existing_nullable=False)
    op.alter_column('teams', 'status',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=16),
               comment='Status of Teams integration: DISABLED, ENABLED, or ACTIVE',
               existing_comment='Status of Teams connection: Disabled, Enabled, Active, or Inactive',
               existing_nullable=False,
               existing_server_default=sa.text("'Disabled'"))
    op.alter_column('teams', 'deleted_at',
               existing_type=mysql.DATETIME(),
               comment='Soft delete timestamp',
               existing_nullable=True)
    op.drop_index('idx_teams_tenant', table_name='teams')
    op.drop_index('idx_teams_user_id', table_name='teams')
    op.drop_index('uq_teams_user_tenant', table_name='teams')
    op.create_unique_constraint('uq_user_team_channel', 'teams', ['user_id', 'team_id', 'channel_id'])
    op.drop_column('teams', 'tenant_id')
    op.drop_column('teams', 'conversation_id')
    op.drop_column('teams', 'service_url')
    op.drop_column('teams', 'conversation_ref_json')


def downgrade() -> None:
    # Reverse Teams OAuth and multi-channel changes
    op.add_column('teams', sa.Column('conversation_ref_json', mysql.JSON(), nullable=False))
    op.add_column('teams', sa.Column('service_url', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=512), nullable=False))
    op.add_column('teams', sa.Column('conversation_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255), nullable=False))
    op.add_column('teams', sa.Column('tenant_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64), nullable=False))
    op.drop_constraint('uq_user_team_channel', 'teams', type_='unique')
    op.create_index('uq_teams_user_tenant', 'teams', ['user_id', 'tenant_id', 'teams_user_id'], unique=True)
    op.create_index('idx_teams_user_id', 'teams', ['teams_user_id'], unique=False)
    op.create_index('idx_teams_tenant', 'teams', ['tenant_id'], unique=False)
    op.alter_column('teams', 'deleted_at',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='Soft delete timestamp',
               existing_nullable=True)
    op.alter_column('teams', 'status',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=16),
               comment='Status of Teams connection: Disabled, Enabled, Active, or Inactive',
               existing_comment='Status of Teams integration: DISABLED, ENABLED, or ACTIVE',
               existing_nullable=False,
               existing_server_default=sa.text("'Disabled'"))
    op.alter_column('teams', 'teams_user_id',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=255),
               comment=None,
               existing_comment='Microsoft Teams user ID',
               existing_nullable=False)
    op.drop_column('teams', 'token_expires_at')
    op.drop_column('teams', 'refresh_token')
    op.drop_column('teams', 'access_token')
    op.drop_column('teams', 'channel_name')
    op.drop_column('teams', 'channel_id')
    op.drop_column('teams', 'team_name')
    op.drop_column('teams', 'team_id')
    op.drop_column('teams', 'username')
    op.drop_column('teams', 'email')
