"""Add oauth_states table for server-side OAuth state validation

Revision ID: 0011_oauth_state
Revises: 0010_domain_not_before
Create Date: 2026-02-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0011_oauth_state'
down_revision = '0010_domain_not_before'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'oauth_states',
        sa.Column('id', sa.String(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('user_id', sa.String(length=36), nullable=False, comment='Foreign key to users table'),
        sa.Column('state_token', sa.String(length=128), nullable=False, comment='Full state string: {user_id}:{uuid}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False, comment='State expires after 10 minutes'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_oauth_states_state_token'), 'oauth_states', ['state_token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_oauth_states_state_token'), table_name='oauth_states')
    op.drop_table('oauth_states')
