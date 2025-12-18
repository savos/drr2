"""add year field to cases table

Revision ID: add_year_to_cases
Revises: add_cases_tables_001
Create Date: 2025-12-17 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_year_to_cases'
down_revision = 'add_cases_tables_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add year column to cases table."""
    # Add year column as nullable first
    op.add_column('cases', sa.Column('year', sa.Integer(), nullable=True, comment='Year the incident occurred'))

    # Update existing records with appropriate years based on known incidents
    op.execute("""
        UPDATE cases SET year = CASE
            WHEN company = 'Microsoft Teams' THEN 2020
            WHEN company = 'Equifax' THEN 2017
            WHEN company = 'O2 UK' THEN 2018
            WHEN company = 'Marketo' THEN 2017
            WHEN company = 'LinkedIn' THEN 2021
            WHEN company = 'Spotify' THEN 2022
            WHEN company = 'Instagram' THEN 2019
            WHEN company = 'Regions Bank' THEN 2016
            WHEN company = 'Foursquare' THEN 2010
            WHEN company = 'NHS UK' THEN 2018
            ELSE 2020
        END
    """)

    # Now make it NOT NULL
    op.alter_column('cases', 'year', nullable=False)


def downgrade() -> None:
    """Remove year column from cases table."""
    op.drop_column('cases', 'year')
