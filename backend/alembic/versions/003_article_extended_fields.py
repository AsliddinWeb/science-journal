"""Add extended fields to articles table

Revision ID: 003_article_extended_fields
Revises: 002_review_system
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('references', postgresql.JSONB(), nullable=True))
    op.add_column('articles', sa.Column('funding', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('conflict_of_interest', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('acknowledgments', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('article_type', sa.String(50), nullable=True))
    op.add_column('articles', sa.Column('cover_letter', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('articles', 'cover_letter')
    op.drop_column('articles', 'article_type')
    op.drop_column('articles', 'acknowledgments')
    op.drop_column('articles', 'conflict_of_interest')
    op.drop_column('articles', 'funding')
    op.drop_column('articles', 'references')
