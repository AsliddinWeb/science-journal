"""Add footer / contact / social fields to home_settings

Revision ID: 012
Revises: 011
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'home_settings',
        sa.Column(
            'footer_description',
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column('home_settings', sa.Column('contact_email', sa.String(length=255), nullable=True))
    op.add_column('home_settings', sa.Column('contact_phone', sa.String(length=100), nullable=True))
    op.add_column('home_settings', sa.Column('contact_address', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_telegram', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_facebook', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_instagram', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_youtube', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_linkedin', sa.String(length=500), nullable=True))
    op.add_column('home_settings', sa.Column('social_twitter', sa.String(length=500), nullable=True))


def downgrade() -> None:
    for col in (
        'social_twitter', 'social_linkedin', 'social_youtube',
        'social_instagram', 'social_facebook', 'social_telegram',
        'contact_address', 'contact_phone', 'contact_email',
        'footer_description',
    ):
        op.drop_column('home_settings', col)
