"""Add site branding fields to home_settings

Revision ID: 011
Revises: 010
"""
from alembic import op
import sqlalchemy as sa


revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('home_settings', sa.Column('site_logo_url', sa.String(length=1000), nullable=True))
    op.add_column(
        'home_settings',
        sa.Column(
            'site_name',
            sa.dialects.postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{\"uz\": \"Filologiya va Ijtimoiy fanlar\", \"ru\": \"Филология и Социальные науки\", \"en\": \"Philology and Social Sciences\"}'::jsonb"),
        ),
    )
    op.add_column(
        'home_settings',
        sa.Column(
            'site_tagline',
            sa.dialects.postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{\"uz\": \"Academicbook\", \"ru\": \"Academicbook\", \"en\": \"Academicbook\"}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column('home_settings', 'site_tagline')
    op.drop_column('home_settings', 'site_name')
    op.drop_column('home_settings', 'site_logo_url')
