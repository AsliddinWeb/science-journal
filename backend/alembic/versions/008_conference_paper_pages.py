"""Add pages field to conference_papers

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('conference_papers', sa.Column('pages', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('conference_papers', 'pages')
