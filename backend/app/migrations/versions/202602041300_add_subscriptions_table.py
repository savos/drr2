"""add subscriptions table

Revision ID: 0017_subscriptions_table
Revises: 0016_pricing_overage_price
Create Date: 2026-02-04 13:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0017_subscriptions_table'
down_revision = '0016_pricing_overage_price'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('billing_cycle', sa.Enum('monthly', 'yearly'), nullable=False, server_default='monthly'),
        sa.Column('status', sa.Enum('active', 'trialing', 'past_due', 'cancelled'), nullable=False, server_default='active'),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('actual_domain_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overage_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['pricing.id']),
    )
    op.create_index('ix_subscriptions_company_id', 'subscriptions', ['company_id'])
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])


def downgrade() -> None:
    op.drop_table('subscriptions')
