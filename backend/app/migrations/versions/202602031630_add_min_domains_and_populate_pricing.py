"""add min_domains and populate pricing

Revision ID: 0012_pricing_min_domains
Revises: 0011_oauth_state
Create Date: 2026-02-03 16:30:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = '0012_pricing_min_domains'
down_revision = '0011_oauth_state'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add min_domains column to pricing table after plan_description
    # MySQL-specific: using raw SQL to specify column position
    op.execute("ALTER TABLE pricing ADD COLUMN min_domains_new INT NOT NULL DEFAULT 0 AFTER plan_description")
    
    # For non-MySQL databases, this would be:
    # op.add_column('pricing', sa.Column('min_domains', sa.Integer(), nullable=False, server_default='0'))

    # Rename the column to remove the _new suffix
    op.execute("ALTER TABLE pricing CHANGE COLUMN min_domains_new min_domains INT NOT NULL")

    # Delete all existing pricing records to avoid conflicts
    op.execute("DELETE FROM pricing")

    # Insert pricing plans
    pricing_plans = [
        {
            'id': str(uuid.uuid4()),
            'name': 'starter',
            'plan_description': 'basic',
            'min_domains': 1,
            'max_domains': 2,
            'monthly_price': 5.0,
            'yearly_price': 50.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'solo',
            'plan_description': 'standard company plan',
            'min_domains': 3,
            'max_domains': 5,
            'monthly_price': 10.0,
            'yearly_price': 100.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'medium',
            'plan_description': 'plan for medium infrastructure',
            'min_domains': 6,
            'max_domains': 10,
            'monthly_price': 20.0,
            'yearly_price': 200.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'big',
            'plan_description': 'plan for extended infrastructure',
            'min_domains': 11,
            'max_domains': 20,
            'monthly_price': 40.0,
            'yearly_price': 400.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'giant',
            'plan_description': 'plan for extremely wide infrastructure',
            'min_domains': 21,
            'max_domains': 35,
            'monthly_price': 70.0,
            'yearly_price': 700.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'agency',
            'plan_description': 'plan for extreme companies and agencies',
            'min_domains': 35,
            'max_domains': 60,
            'monthly_price': 120.0,
            'yearly_price': 1200.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]

    # Insert all pricing plans
    pricing_table = sa.table('pricing',
        sa.column('id', sa.String(36)),
        sa.column('name', sa.String(255)),
        sa.column('plan_description', sa.Text),
        sa.column('min_domains', sa.Integer),
        sa.column('max_domains', sa.Integer),
        sa.column('monthly_price', sa.Float),
        sa.column('yearly_price', sa.Float),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )

    op.bulk_insert(pricing_table, pricing_plans)


def downgrade() -> None:
    # Remove the min_domains column
    op.drop_column('pricing', 'min_domains')

    # Note: This does not restore the previous pricing data
    # You may want to backup the pricing table before running this migration
