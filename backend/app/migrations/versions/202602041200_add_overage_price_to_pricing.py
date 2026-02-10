"""add per_domain_overage_price to pricing

Revision ID: 0016_pricing_overage_price
Revises: 0015_pricing_id_to_int
Create Date: 2026-02-04 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0016_pricing_overage_price'
down_revision = '0015_pricing_id_to_int'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add per_domain_overage_price column (nullable — only set for open-ended plans)
    op.add_column('pricing', sa.Column('per_domain_overage_price', sa.Float(), nullable=True))

    # Set $2/domain overage rate on the agency plan (max_domains IS NULL)
    op.execute("UPDATE pricing SET per_domain_overage_price = 2.0 WHERE max_domains IS NULL")


def downgrade() -> None:
    op.drop_column('pricing', 'per_domain_overage_price')
