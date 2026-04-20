"""Add theme column to home_settings

Revision ID: 009
Revises: 008
"""
from alembic import op
import sqlalchemy as sa


revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'home_settings',
        sa.Column('theme', sa.String(length=50), nullable=False, server_default='indigo'),
    )


def downgrade() -> None:
    op.drop_column('home_settings', 'theme')
