"""Add email verification code
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_email_verification'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add verification fields to users table
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('verification_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('verification_code_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Drop verification fields
    op.drop_column('users', 'verification_code_expires_at')
    op.drop_column('users', 'verification_code')
    op.drop_column('users', 'is_verified')
