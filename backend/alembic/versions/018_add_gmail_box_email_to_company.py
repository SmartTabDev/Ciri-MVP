"""add gmail_box_email to company
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('companies', sa.Column('gmail_box_email', sa.String(length=100), nullable=True))

def downgrade() -> None:
    op.drop_column('companies', 'gmail_box_email')
