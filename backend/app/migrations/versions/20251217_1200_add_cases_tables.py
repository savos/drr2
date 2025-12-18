"""add cases and cases_links tables

Revision ID: add_cases_tables_001
Revises: c19127697080
Create Date: 2025-12-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_cases_tables_001'
down_revision = 'c19127697080'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create cases and cases_links tables."""

    # Create cases table
    op.create_table(
        'cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company', sa.String(length=32), nullable=False),
        sa.Column(
            'problem',
            sa.Enum('Domain', 'SSL', 'Domain, SSL', name='problemtype', native_enum=False, length=20),
            nullable=False,
            comment='Type of problem: Domain, SSL, or Domain, SSL'
        ),
        sa.Column('heading', sa.String(length=64), nullable=False),
        sa.Column('text', sa.String(length=256), nullable=False),
        sa.Column('loss', sa.String(length=128), nullable=True, comment='Financial or reputation loss amount'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create cases_links table
    op.create_table(
        'cases_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('link', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], name='cases_links_ibfk_case', ondelete='CASCADE'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create index for better query performance
    op.create_index('idx_cases_links_case_id', 'cases_links', ['case_id'], unique=False)


def downgrade() -> None:
    """Drop cases and cases_links tables."""
    op.drop_index('idx_cases_links_case_id', table_name='cases_links')
    op.drop_table('cases_links')
    op.drop_table('cases')
