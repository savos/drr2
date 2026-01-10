"""Add unique constraints to prevent duplicate cases and links

Revision ID: 0003_unique_cases_links
Revises: 0002_teams_conversations
Create Date: 2026-01-07 03:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0003_unique_cases_links'
down_revision = '0002_teams_conversations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique constraint on cases to minimize duplicates
    # Using (company, problem, year, heading) to allow distinct incidents
    op.create_unique_constraint(
        'uq_cases_company_problem_year_heading',
        'cases',
        ['company', 'problem', 'year', 'heading']
    )

    # Add unique constraint on cases_links per case_id+link
    op.create_unique_constraint(
        'uq_cases_links_case_link',
        'cases_links',
        ['case_id', 'link']
    )


def downgrade() -> None:
    op.drop_constraint('uq_cases_links_case_link', 'cases_links', type_='unique')
    op.drop_constraint('uq_cases_company_problem_year_heading', 'cases', type_='unique')

