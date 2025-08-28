"""add email context

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('leads', sa.Column('email_context', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('leads', 'email_context') 