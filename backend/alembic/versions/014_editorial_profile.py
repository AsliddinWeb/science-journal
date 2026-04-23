"""Extend editorial_board_members profile fields

Revision ID: 014
Revises: 013
"""
from alembic import op
import sqlalchemy as sa


revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


NEW_COLUMNS = [
    ('email', sa.String(length=255)),
    ('degree', sa.String(length=100)),
    ('specialization', sa.String(length=500)),
    ('scopus_id', sa.String(length=50)),
    ('researcher_id', sa.String(length=50)),
    ('google_scholar_url', sa.String(length=500)),
    ('website_url', sa.String(length=500)),
]


def upgrade() -> None:
    for name, col_type in NEW_COLUMNS:
        op.add_column('editorial_board_members', sa.Column(name, col_type, nullable=True))


def downgrade() -> None:
    for name, _ in reversed(NEW_COLUMNS):
        op.drop_column('editorial_board_members', name)
