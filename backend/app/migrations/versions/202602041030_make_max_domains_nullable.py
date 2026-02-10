"""make max_domains nullable

Revision ID: 0014_max_domains_nullable
Revises: 0013_pricing_max_users
Create Date: 2026-02-04 10:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0014_max_domains_nullable'
down_revision = '0013_pricing_max_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make max_domains nullable (MySQL-specific syntax)
    op.execute("ALTER TABLE pricing MODIFY COLUMN max_domains INT NULL")


def downgrade() -> None:
    # Make max_domains NOT NULL again
    # Note: This will fail if there are NULL values in the column
    op.execute("ALTER TABLE pricing MODIFY COLUMN max_domains INT NOT NULL")
