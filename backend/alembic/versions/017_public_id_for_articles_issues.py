"""Add integer public_id to articles and issues for OJS-style short URLs.

UUIDs stay as the internal primary key (FKs all reference them); public_id
is what shows up in `/article/view/<n>` and `/issue/view/<n>`. The API
accepts either form so old UUID links keep working.

Revision ID: 017
Revises: 016
"""
from alembic import op
import sqlalchemy as sa


revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def _add_public_id(table: str, seq: str, order_by: str) -> None:
    op.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq}")
    op.add_column(
        table,
        sa.Column(
            'public_id',
            sa.Integer(),
            nullable=True,
            server_default=sa.text(f"nextval('{seq}'::regclass)"),
        ),
    )
    # Backfill existing rows with sequential numbers ordered by creation time.
    op.execute(
        f"""
        WITH numbered AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY {order_by}, id) AS rn
            FROM {table}
        )
        UPDATE {table} t SET public_id = n.rn FROM numbered n WHERE t.id = n.id
        """
    )
    # Advance the sequence past the highest backfilled value so future inserts
    # don't collide.
    op.execute(
        f"""
        SELECT setval('{seq}',
            COALESCE((SELECT MAX(public_id) FROM {table}), 0) + 1,
            false)
        """
    )
    op.alter_column(table, 'public_id', nullable=False)
    op.create_unique_constraint(f'uq_{table}_public_id', table, ['public_id'])
    op.create_index(f'ix_{table}_public_id', table, ['public_id'])


def _drop_public_id(table: str, seq: str) -> None:
    op.drop_index(f'ix_{table}_public_id', table_name=table)
    op.drop_constraint(f'uq_{table}_public_id', table, type_='unique')
    op.drop_column(table, 'public_id')
    op.execute(f"DROP SEQUENCE IF EXISTS {seq}")


def upgrade() -> None:
    _add_public_id('articles', 'articles_public_id_seq', 'created_at')
    _add_public_id('issues', 'issues_public_id_seq', 'created_at')


def downgrade() -> None:
    _drop_public_id('issues', 'issues_public_id_seq')
    _drop_public_id('articles', 'articles_public_id_seq')
