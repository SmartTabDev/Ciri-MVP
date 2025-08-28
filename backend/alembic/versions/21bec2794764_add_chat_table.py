"""add chat table

Revision ID: 21bec2794764
Revises: 020
Create Date: 2025-07-25 10:35:59.180483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21bec2794764'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'chat',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('thread_id', sa.String(), index=True),
        sa.Column('message_id', sa.String(), unique=True, index=True),
        sa.Column('from_email', sa.String(), index=True),
        sa.Column('to_email', sa.String()),
        sa.Column('subject', sa.String()),
        sa.Column('body_text', sa.Text()),
        sa.Column('body_html', sa.Text()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_incoming', sa.Boolean(), default=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('chat')
