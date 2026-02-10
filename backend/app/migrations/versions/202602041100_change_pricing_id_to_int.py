"""change pricing id to int autoincrement

Revision ID: 0015_pricing_id_to_int
Revises: 0014_max_domains_nullable
Create Date: 2026-02-04 11:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0015_pricing_id_to_int'
down_revision = '0014_max_domains_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add temporary new_id column to pricing table
    op.execute("ALTER TABLE pricing ADD COLUMN new_id INT UNIQUE")

    # Step 2: Populate new_id with sequential values
    op.execute("SET @row_number = 0")
    op.execute("""
        UPDATE pricing SET new_id = (@row_number := @row_number + 1)
        ORDER BY created_at
    """)

    # Step 3: Add temporary new_price_plan_id column to companies table
    op.execute("ALTER TABLE companies ADD COLUMN new_price_plan_id INT NULL")

    # Step 4: Update companies table references using the mapping
    op.execute("""
        UPDATE companies c
        INNER JOIN pricing p ON c.price_plan_id = p.id
        SET c.new_price_plan_id = p.new_id
        WHERE c.price_plan_id IS NOT NULL
    """)

    # Step 5: Drop foreign key constraint
    op.execute("ALTER TABLE companies DROP FOREIGN KEY companies_ibfk_1")

    # Step 6: Drop old columns
    op.execute("ALTER TABLE companies DROP COLUMN price_plan_id")
    op.execute("ALTER TABLE pricing DROP PRIMARY KEY")
    op.execute("ALTER TABLE pricing DROP COLUMN id")

    # Step 7: Rename new_id to id and make it AUTO_INCREMENT PRIMARY KEY
    op.execute("ALTER TABLE pricing CHANGE COLUMN new_id id INT AUTO_INCREMENT PRIMARY KEY FIRST")
    
    # Step 8: Rename new_price_plan_id to price_plan_id
    op.execute("ALTER TABLE companies CHANGE COLUMN new_price_plan_id price_plan_id INT NULL")

    # Step 9: Recreate foreign key constraint
    op.execute("""
        ALTER TABLE companies
        ADD CONSTRAINT companies_ibfk_1
        FOREIGN KEY (price_plan_id) REFERENCES pricing(id)
    """)

    # Step 10: Ensure index exists on price_plan_id
    op.execute("CREATE INDEX ix_companies_price_plan_id ON companies(price_plan_id)")


def downgrade() -> None:
    # This is a destructive change that cannot be easily reversed
    # as we lose the UUID values
    raise NotImplementedError("Downgrade from INT to UUID is not supported")
