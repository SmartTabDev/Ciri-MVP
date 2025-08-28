"""Add foreign key constraint to channel_context table

Revision ID: add_foreign_key_to_channel_context
Revises: 74d59b797615
Create Date: 2025-08-07 10:37:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fk_channel_context'
down_revision = '74d59b797615'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_channel_context_company_id',
        'channel_context',
        'companies',
        ['company_id'],
        ['id']
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint(
        'fk_channel_context_company_id',
        'channel_context',
        type_='foreignkey'
    ) 