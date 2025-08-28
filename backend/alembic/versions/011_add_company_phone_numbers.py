"""add phone_numbers to company

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('companies', sa.Column('phone_numbers', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('companies', 'phone_numbers') 