"""Add terms_of_service and business_category to company table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add terms_of_service and business_category columns to company table
    op.add_column('companies', sa.Column('terms_of_service', sa.Text(), nullable=False, server_default="Default Terms of Service"))
    op.add_column('companies', sa.Column('business_category', sa.String(), nullable=False, server_default="Other"))


def downgrade() -> None:
    # Remove terms_of_service and business_category columns from company table
    op.drop_column('companies', 'terms_of_service')
    op.drop_column('companies', 'business_category') 