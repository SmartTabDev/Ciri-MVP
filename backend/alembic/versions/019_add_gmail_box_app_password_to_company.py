"""
Add gmail_box_app_password column to companies table
"""
# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('companies', sa.Column('gmail_box_app_password', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('companies', 'gmail_box_app_password') 