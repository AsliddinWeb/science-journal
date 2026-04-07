"""Add cover_image_url to volumes

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('volumes', sa.Column('cover_image_url', sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column('volumes', 'cover_image_url')
