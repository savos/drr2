"""Update pricing plan descriptions to be marketing-friendly

Revision ID: 0018_pricing_descriptions
Revises: 0017_subscriptions_table
Create Date: 2026-02-10 10:00:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '0018_pricing_descriptions'
down_revision = '0017_subscriptions_table'
branch_labels = None
depends_on = None

DESCRIPTIONS = [
    ('starter',  'Perfect for individuals tracking a couple of domains. Get uptime alerts and SSL expiry notifications right away.'),
    ('mini',     'Great for small projects and freelancers. Monitor up to 5 domains with instant multi-channel alerts.'),
    ('team',     'Ideal for growing teams. Collaborate with up to 5 users and keep tabs on up to 9 domains together.'),
    ('medium',   'Built for busy businesses. Monitor up to 15 domains/SSLs with your team and never miss a critical event.'),
    ('pro',      'For power users who need more coverage. 24 domains, advanced integrations, and full alert customization.'),
    ('big',      'Scale up your monitoring across 37 domains. Includes automation integrations and priority support.'),
    ('large',    'Enterprise-grade coverage for up to 49 domains with full integration support and priority response.'),
    ('agency',   'Unlimited scale for agencies and large organisations. Start at 50 domains — add more at just $2 each.'),
]


def upgrade() -> None:
    for name, description in DESCRIPTIONS:
        op.execute(
            f"UPDATE pricing SET plan_description = '{description}' WHERE name = '{name}'"
        )


def downgrade() -> None:
    pass
