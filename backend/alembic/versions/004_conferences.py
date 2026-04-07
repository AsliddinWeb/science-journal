"""Add conferences feature and article cover_image_url

Revision ID: 004
Revises: 003
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type directly with raw SQL
    op.execute("CREATE TYPE conferencespaperstatus AS ENUM ('draft', 'submitted', 'accepted', 'rejected', 'published')")

    # --- conferences ---
    op.execute("""
        CREATE TABLE conferences (
            id UUID PRIMARY KEY,
            title JSONB NOT NULL,
            description JSONB,
            location VARCHAR(500),
            start_date DATE,
            end_date DATE,
            year INTEGER NOT NULL,
            cover_image_url VARCHAR(1000),
            is_active BOOLEAN NOT NULL DEFAULT true,
            organizer VARCHAR(500),
            website_url VARCHAR(1000),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.create_index('ix_conferences_year', 'conferences', ['year'])

    # --- conference_sessions ---
    op.execute("""
        CREATE TABLE conference_sessions (
            id UUID PRIMARY KEY,
            conference_id UUID NOT NULL REFERENCES conferences(id) ON DELETE CASCADE,
            title JSONB NOT NULL,
            description JSONB,
            "order" INTEGER NOT NULL DEFAULT 1,
            date DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.create_index('ix_conference_sessions_conference_id', 'conference_sessions', ['conference_id'])

    # --- conference_papers ---
    op.execute("""
        CREATE TABLE conference_papers (
            id UUID PRIMARY KEY,
            title JSONB NOT NULL,
            abstract JSONB NOT NULL,
            keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
            language VARCHAR(10) NOT NULL DEFAULT 'uz',
            conference_id UUID NOT NULL REFERENCES conferences(id) ON DELETE CASCADE,
            session_id UUID REFERENCES conference_sessions(id),
            author_id UUID NOT NULL REFERENCES users(id),
            doi VARCHAR(255) UNIQUE,
            pdf_file_path VARCHAR(1000),
            pdf_file_size INTEGER,
            cover_image_url VARCHAR(1000),
            status conferencespaperstatus NOT NULL DEFAULT 'draft',
            published_date TIMESTAMPTZ,
            download_count INTEGER NOT NULL DEFAULT 0,
            view_count INTEGER NOT NULL DEFAULT 0,
            "references" JSONB,
            funding TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.create_index('ix_conference_papers_conference_id', 'conference_papers', ['conference_id'])
    op.create_index('ix_conference_papers_session_id', 'conference_papers', ['session_id'])
    op.create_index('ix_conference_papers_author_id', 'conference_papers', ['author_id'])
    op.create_index('ix_conference_papers_status', 'conference_papers', ['status'])
    op.create_index('ix_conference_papers_doi', 'conference_papers', ['doi'])

    # --- conference_paper_authors ---
    op.execute("""
        CREATE TABLE conference_paper_authors (
            id UUID PRIMARY KEY,
            paper_id UUID NOT NULL REFERENCES conference_papers(id) ON DELETE CASCADE,
            user_id UUID REFERENCES users(id),
            guest_name VARCHAR(255),
            guest_email VARCHAR(255),
            guest_affiliation VARCHAR(500),
            guest_orcid VARCHAR(50),
            "order" INTEGER NOT NULL DEFAULT 1,
            is_corresponding BOOLEAN NOT NULL DEFAULT false
        )
    """)
    op.create_index('ix_conference_paper_authors_paper_id', 'conference_paper_authors', ['paper_id'])

    # --- Add cover_image_url to articles ---
    op.add_column('articles', sa.Column('cover_image_url', sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column('articles', 'cover_image_url')
    op.drop_table('conference_paper_authors')
    op.drop_table('conference_papers')
    op.drop_table('conference_sessions')
    op.drop_table('conferences')
    op.execute('DROP TYPE IF EXISTS conferencespaperstatus')
