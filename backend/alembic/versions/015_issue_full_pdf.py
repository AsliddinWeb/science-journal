"""Add full_pdf_url to issues — combined issue PDF

Revision ID: 015
Revises: 014
"""
from alembic import op
import sqlalchemy as sa


revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('issues', sa.Column('full_pdf_url', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column('issues', 'full_pdf_url')
