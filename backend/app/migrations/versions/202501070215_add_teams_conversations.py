"""Add Teams conversations table for bot proactive messaging

Revision ID: 0002_teams_conversations
Revises: 0001_initial
Create Date: 2026-01-07 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '0002_teams_conversations'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'teams_conversations',
        sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('scope', sa.String(length=16), nullable=False, comment='Scope: personal or team'),
        sa.Column('service_url', sa.Text(), nullable=False, comment='Bot Framework serviceUrl'),
        sa.Column('conversation_id', sa.String(length=255), nullable=False, comment='Conversation ID for proactive messages'),
        sa.Column('team_id', sa.String(length=255), nullable=True, comment='Team ID if scope=team'),
        sa.Column('channel_id', sa.String(length=255), nullable=True, comment='Channel ID if scope=team'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id', name='uq_conversation_id'),
    )


def downgrade() -> None:
    op.drop_table('teams_conversations')

