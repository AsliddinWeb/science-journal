"""Add Phase 4 review system fields

Revision ID: 002
Revises: 001
Create Date: 2026-03-26 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reviews", sa.Column("editor_comments", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("decline_reason", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("invitation_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("reviews", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("reviews", sa.Column("declined_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("reviews", "declined_at")
    op.drop_column("reviews", "accepted_at")
    op.drop_column("reviews", "invitation_sent_at")
    op.drop_column("reviews", "decline_reason")
    op.drop_column("reviews", "editor_comments")
