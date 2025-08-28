"""Add company table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '003_email_verification'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create company table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('follow_up_cycle', sa.Integer(), nullable=True),
        sa.Column('calendar_link', sa.String(), nullable=True),
        sa.Column('business_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)
    
    # Add company_id to users table
    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_company_id', 'users', 'companies', ['company_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_users_company_id', 'users', type_='foreignkey')
    
    # Drop company_id column from users table
    op.drop_column('users', 'company_id')
    
    # Drop company table
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
