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


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("cases")}
    if "year" not in cols:
        op.add_column(
            "cases",
            sa.Column(
                "year",
                sa.Integer(),
                nullable=True,
                comment="Year the incident occurred",
            ),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("cases")}
    if "year" in cols:
        op.drop_column("cases", "year")

