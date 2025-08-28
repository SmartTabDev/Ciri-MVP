"""Remove calendar_link from company table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove calendar_link column from company table
    op.drop_column('companies', 'calendar_link')


def downgrade() -> None:
    # Add calendar_link column back to company table
    op.add_column('companies', sa.Column('calendar_link', sa.String(), nullable=True)) 