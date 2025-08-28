"""Add calendar credentials to company table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add calendar credentials column to company table
    op.add_column('companies', sa.Column('calendar_credentials', JSON, nullable=True))


def downgrade() -> None:
    # Remove calendar credentials column from company table
    op.drop_column('companies', 'calendar_credentials') 