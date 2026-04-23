"""Allow NULL author_id for articles and conference_papers — enables guest authors

Revision ID: 013
Revises: 012
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'articles', 'author_id',
        existing_type=postgresql.UUID(),
        nullable=True,
    )
    op.alter_column(
        'conference_papers', 'author_id',
        existing_type=postgresql.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'articles', 'author_id',
        existing_type=postgresql.UUID(),
        nullable=False,
    )
    op.alter_column(
        'conference_papers', 'author_id',
        existing_type=postgresql.UUID(),
        nullable=False,
    )
