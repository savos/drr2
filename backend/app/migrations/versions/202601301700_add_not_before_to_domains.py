"""Add not_before field to domains table for SSL certificates

Revision ID: 0010_domain_not_before
Revises: 0009_domains_table
Create Date: 2026-01-30 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0010_domain_not_before'
down_revision = '0009_domains_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add not_before column after renew_date
    op.add_column(
        'domains',
        sa.Column('not_before', sa.DateTime(), nullable=True, comment='SSL certificate valid from date')
    )


def downgrade() -> None:
    op.drop_column('domains', 'not_before')
