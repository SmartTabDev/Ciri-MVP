"""Add goal field to AI agent settings table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add goal column to ai_agent_settings table
    op.add_column(
        'ai_agent_settings',
        sa.Column('goal', sa.String(), nullable=False, server_default="Book appointments and collect customer emails")
    )


def downgrade() -> None:
    # Remove goal column from ai_agent_settings table
    op.drop_column('ai_agent_settings', 'goal') 