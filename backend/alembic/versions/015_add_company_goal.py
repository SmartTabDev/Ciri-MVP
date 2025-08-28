"""add company goal
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add goal column to companies table
    op.add_column('companies', sa.Column('goal', sa.String(500), nullable=False,
                  server_default='Book appointments and collect customer emails'))


def downgrade() -> None:
    # Remove goal column from companies table
    op.drop_column('companies', 'goal') 