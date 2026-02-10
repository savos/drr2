"""add max_users to pricing

Revision ID: 0013_pricing_max_users
Revises: 0012_pricing_min_domains
Create Date: 2026-02-04 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0013_pricing_max_users'
down_revision = '0012_pricing_min_domains'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add max_users column after max_domains (MySQL-specific AFTER clause)
    op.execute("ALTER TABLE pricing ADD COLUMN max_users INT NOT NULL DEFAULT 1 AFTER max_domains")


def downgrade() -> None:
    op.drop_column('pricing', 'max_users')
