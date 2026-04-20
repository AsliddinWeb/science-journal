"""Add hero video fields to home_settings

Revision ID: 010
Revises: 009
"""
from alembic import op
import sqlalchemy as sa


revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('home_settings', sa.Column('hero_video_url', sa.String(length=1000), nullable=True))
    op.add_column('home_settings', sa.Column('hero_video_poster_url', sa.String(length=1000), nullable=True))
    op.add_column(
        'home_settings',
        sa.Column('hero_video_active', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('home_settings', 'hero_video_active')
    op.drop_column('home_settings', 'hero_video_poster_url')
    op.drop_column('home_settings', 'hero_video_url')
