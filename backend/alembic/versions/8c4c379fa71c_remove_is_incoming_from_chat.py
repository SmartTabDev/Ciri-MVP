"""remove_is_incoming_from_chat

Revision ID: 8c4c379fa71c
Revises: 39dccaae8947
Create Date: 2025-07-28 10:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c4c379fa71c'
down_revision = '39dccaae8947'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove the is_incoming column from chat table
    op.drop_column('chat', 'is_incoming')


def downgrade() -> None:
    # Add back the is_incoming column to chat table
    op.add_column('chat', sa.Column('is_incoming', sa.BOOLEAN(), nullable=True, default=True))
