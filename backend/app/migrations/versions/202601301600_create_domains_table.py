"""Create domains table for domain and SSL monitoring

Revision ID: 0009_domains_table
Revises: 0008_password_nullable
Create Date: 2026-01-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0009_domains_table'
down_revision = '0008_password_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'domains',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False, comment='Foreign key to companies table'),
        sa.Column('name', sa.String(length=256), nullable=False, comment='Domain name or IP address'),
        sa.Column('type', sa.Enum('DOMAIN', 'SSL', name='domaintype'), nullable=False, comment='Type: DOMAIN or SSL'),
        sa.Column('renew_date', sa.Date(), nullable=False, comment='Date when service expires'),
        sa.Column('issuer', sa.String(length=128), nullable=False, comment='Who issued the service (registrar/CA)'),
        sa.Column('issuer_link', sa.String(length=512), nullable=True, comment='Website of issuer'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='When record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False, comment='When domain/SSL was last checked'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index(op.f('ix_domains_company_id'), 'domains', ['company_id'], unique=False)
    op.create_index(op.f('ix_domains_renew_date'), 'domains', ['renew_date'], unique=False)
    op.create_index(op.f('ix_domains_type'), 'domains', ['type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_domains_type'), table_name='domains')
    op.drop_index(op.f('ix_domains_renew_date'), table_name='domains')
    op.drop_index(op.f('ix_domains_company_id'), table_name='domains')
    op.drop_table('domains')

    # Drop the enum type (PostgreSQL specific - MySQL will ignore this)
    op.execute('DROP TYPE IF EXISTS domaintype')
