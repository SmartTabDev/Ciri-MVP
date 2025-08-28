"""remove username from users table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '017'
down_revision: Union[str, None] = '016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')

def downgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    op.create_index('ix_users_username', 'users', ['username'], unique=True) 