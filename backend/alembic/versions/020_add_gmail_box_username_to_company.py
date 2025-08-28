"""
Add gmail_box_username column to companies table
"""
# revision identifiers, used by Alembic.
revision = '020'
down_revision = '171e4584d011'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('companies', sa.Column('gmail_box_username', sa.String(length=200), nullable=True))

def downgrade():
    op.drop_column('companies', 'gmail_box_username') 