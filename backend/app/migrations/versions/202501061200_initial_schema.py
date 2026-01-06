"""Initial schema - all tables

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pricing table first (no dependencies)
    op.create_table('pricing',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('plan_description', sa.Text(), nullable=False),
        sa.Column('max_domains', sa.Integer(), nullable=False),
        sa.Column('monthly_price', sa.Float(), nullable=False),
        sa.Column('yearly_price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create companies table (depends on pricing)
    op.create_table('companies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('payable', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('price_plan_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['price_plan_id'], ['pricing.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table (depends on companies)
    op.create_table('users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('firstname', sa.String(length=64), nullable=False),
        sa.Column('lastname', sa.String(length=64), nullable=False),
        sa.Column('position', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=64), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('verified', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_superuser', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notifications', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('slack', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('teams', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('discord', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('telegram', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create cases table (no foreign key dependencies on main tables)
    op.create_table('cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company', sa.String(length=32), nullable=False),
        sa.Column('problem', sa.String(length=20), nullable=False, comment='Type of problem: Domain, SSL, or Domain, SSL'),
        sa.Column('year', sa.Integer(), nullable=False, comment='Year the incident occurred'),
        sa.Column('heading', sa.String(length=64), nullable=False),
        sa.Column('text', sa.String(length=256), nullable=False),
        sa.Column('loss', sa.String(length=128), nullable=True, comment='Financial or reputation loss amount'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cases_links table (depends on cases)
    op.create_table('cases_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('link', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create slack table (depends on users)
    op.create_table('slack',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('workspace_id', sa.CHAR(length=36), nullable=False),
        sa.Column('workspace_name', sa.String(length=128), nullable=True),
        sa.Column('bot_token', sa.Text(), nullable=False),
        sa.Column('bot_user_id', sa.String(length=32), nullable=True),
        sa.Column('slack_user_id', sa.String(length=32), nullable=True),
        sa.Column('channel_id', sa.String(length=32), nullable=False, comment='DM channel ID (slack_user_id) or group channel ID'),
        sa.Column('channel_name', sa.String(length=255), nullable=True, comment='Channel name for group channels, NULL for DMs'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Disabled', comment='Status of Slack integration: Disabled, Enabled, or Active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create telegram table (depends on users)
    op.create_table('telegram',
        sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=True, comment='Telegram user ID who connected this chat'),
        sa.Column('channel_id', sa.BigInteger(), nullable=False, comment='Chat ID: user chat_id for DMs, group chat_id for groups'),
        sa.Column('chat_type', sa.String(length=20), nullable=False, server_default='private', comment='Type of chat: private, group, supergroup, or channel'),
        sa.Column('chat_title', sa.String(length=255), nullable=True, comment='Chat title for groups/channels, NULL for DMs'),
        sa.Column('username', sa.String(length=255), nullable=True, comment='User Telegram username'),
        sa.Column('first_name', sa.String(length=255), nullable=True, comment='User first name'),
        sa.Column('last_name', sa.String(length=255), nullable=True, comment='User last name'),
        sa.Column('language_code', sa.String(length=16), nullable=True, comment='User language code'),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='DISABLED', comment='Status of Telegram integration: DISABLED, ENABLED, or ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create discord table (depends on users)
    op.create_table('discord',
        sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('discord_user_id', sa.String(length=32), nullable=False, comment='Discord user ID'),
        sa.Column('guild_id', sa.String(length=32), nullable=True, comment='Discord server (guild) ID - NULL for DMs'),
        sa.Column('guild_name', sa.String(length=255), nullable=True, comment='Discord server (guild) name - NULL for DMs'),
        sa.Column('channel_id', sa.String(length=32), nullable=True, comment='Discord channel ID - NULL for DMs'),
        sa.Column('channel_name', sa.String(length=255), nullable=True, comment='Discord channel name - NULL for DMs'),
        sa.Column('username', sa.String(length=255), nullable=True, comment='Discord username'),
        sa.Column('global_name', sa.String(length=255), nullable=True, comment='Discord display name'),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='DISABLED', comment='Status of Discord integration: DISABLED, ENABLED, or ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'guild_id', 'channel_id', name='uq_user_guild_channel')
    )

    # Create teams table (depends on users)
    op.create_table('teams',
        sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('teams_user_id', sa.String(length=255), nullable=False, comment='Microsoft Teams user ID'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='User email address'),
        sa.Column('username', sa.String(length=255), nullable=True, comment='User display name'),
        sa.Column('team_id', sa.String(length=255), nullable=True, comment='Teams team ID - NULL for DMs'),
        sa.Column('team_name', sa.String(length=255), nullable=True, comment='Teams team name - NULL for DMs'),
        sa.Column('channel_id', sa.String(length=255), nullable=True, comment='Teams channel ID - NULL for DMs'),
        sa.Column('channel_name', sa.String(length=255), nullable=True, comment='Teams channel name - NULL for DMs'),
        sa.Column('access_token', sa.Text(), nullable=True, comment='Encrypted OAuth access token'),
        sa.Column('refresh_token', sa.Text(), nullable=True, comment='Encrypted OAuth refresh token'),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True, comment='Access token expiration timestamp'),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='DISABLED', comment='Status of Teams integration: DISABLED, ENABLED, or ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'team_id', 'channel_id', name='uq_user_team_channel')
    )


def downgrade() -> None:
    op.drop_table('teams')
    op.drop_table('discord')
    op.drop_table('telegram')
    op.drop_table('slack')
    op.drop_table('cases_links')
    op.drop_table('cases')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('companies')
    op.drop_table('pricing')
