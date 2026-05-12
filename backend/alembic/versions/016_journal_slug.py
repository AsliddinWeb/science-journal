"""Add journal_slug to home_settings for the public home-route URL.

Revision ID: 016
Revises: 015
"""
from alembic import op
import sqlalchemy as sa


revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'home_settings',
        sa.Column(
            'journal_slug',
            sa.String(length=100),
            nullable=False,
            server_default='academic-book-journal',
        ),
    )


def downgrade() -> None:
    op.drop_column('home_settings', 'journal_slug')
