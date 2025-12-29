"""fix_discord_constraints

Revision ID: 1d3966e77f4b
Revises: 30057e622415
Create Date: 2025-12-24 16:55:17.207693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d3966e77f4b'
down_revision = '30057e622415'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old unique constraint that prevents multiple integrations
    op.drop_constraint('uq_discord_user_account', 'discord', type_='unique')

    # Add new unique constraint for multi-channel support
    op.create_unique_constraint('uq_user_guild_channel', 'discord', ['user_id', 'guild_id', 'channel_id'])


def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint('uq_user_guild_channel', 'discord', type_='unique')
    op.create_unique_constraint('uq_discord_user_account', 'discord', ['user_id', 'discord_user_id'])
