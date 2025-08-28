"""Add AI agent settings table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_agent_settings table
    op.create_table(
        'ai_agent_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('voice_type', sa.String(), nullable=False),
        sa.Column('dialect', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_agent_settings_id'), 'ai_agent_settings', ['id'], unique=False)
    op.create_foreign_key('fk_ai_agent_settings_company_id', 'ai_agent_settings', 'companies', ['company_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_ai_agent_settings_company_id', 'ai_agent_settings', type_='foreignkey')
    
    # Drop ai_agent_settings table
    op.drop_index(op.f('ix_ai_agent_settings_id'), table_name='ai_agent_settings')
    op.drop_table('ai_agent_settings') 