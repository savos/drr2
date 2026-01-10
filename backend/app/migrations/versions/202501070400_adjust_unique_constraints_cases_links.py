"""Adjust unique constraints: cases(company,problem,year), cases_links(link)

Revision ID: 0004_adjust_uniques
Revises: 0003_unique_cases_links
Create Date: 2026-01-07 04:00:00.000000

"""
from alembic import op


revision = '0004_adjust_uniques'
down_revision = '0003_unique_cases_links'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop previous constraints if they exist
    try:
        op.drop_constraint('uq_cases_company_problem_year_heading', 'cases', type_='unique')
    except Exception:
        pass
    try:
        op.drop_constraint('uq_cases_links_case_link', 'cases_links', type_='unique')
    except Exception:
        pass

    # Add requested constraints
    op.create_unique_constraint(
        'uq_cases_company_problem_year', 'cases', ['company', 'problem', 'year']
    )
    op.create_unique_constraint(
        'uq_cases_links_link', 'cases_links', ['link']
    )


def downgrade() -> None:
    op.drop_constraint('uq_cases_links_link', 'cases_links', type_='unique')
    op.drop_constraint('uq_cases_company_problem_year', 'cases', type_='unique')
    # Restore previous, broader constraints
    op.create_unique_constraint(
        'uq_cases_company_problem_year_heading', 'cases', ['company', 'problem', 'year', 'heading']
    )
    op.create_unique_constraint(
        'uq_cases_links_case_link', 'cases_links', ['case_id', 'link']
    )

