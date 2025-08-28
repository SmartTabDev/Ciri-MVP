"""add follow up last sent at

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('leads', sa.Column('follow_up_last_sent_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('leads', 'follow_up_last_sent_at') 