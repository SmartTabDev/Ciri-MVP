"""add_email_provider_to_chat

Revision ID: fba6e0aeb404
Revises: 723a4a35fc2b
Create Date: 2025-08-10 15:01:35.555494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fba6e0aeb404'
down_revision = '723a4a35fc2b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email_provider column to chat table
    op.add_column('chat', sa.Column('email_provider', sa.String(50), nullable=True))


def downgrade() -> None:
    # Remove email_provider column from chat table
    op.drop_column('chat', 'email_provider')
