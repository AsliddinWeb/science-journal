"""Add journal_abbrev to home_settings for citation_journal_abbrev meta tag.

The short journal abbreviation that Scholar / OJS exposes as
`citation_journal_abbrev` (e.g. "IGSIIT"). Editor-supplied — there's
no reliable way to derive it from the long multilingual title.

Revision ID: 018
Revises: 017
"""
from alembic import op
import sqlalchemy as sa


revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'home_settings',
        sa.Column('journal_abbrev', sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('home_settings', 'journal_abbrev')
