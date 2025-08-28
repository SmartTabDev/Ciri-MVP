"""rename_thread_id_to_channel_id

Revision ID: 723a4a35fc2b
Revises: add_fk_channel_context
Create Date: 2025-08-10 14:33:56.513856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '723a4a35fc2b'
down_revision = 'add_fk_channel_context'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename thread_id column to channel_id in chat table
    op.alter_column('chat', 'thread_id', new_column_name='channel_id')


def downgrade() -> None:
    # Rename channel_id column back to thread_id in chat table
    op.alter_column('chat', 'channel_id', new_column_name='thread_id')
