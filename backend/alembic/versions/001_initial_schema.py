"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("superadmin", "editor", "reviewer", "author", "reader", name="userrole"),
            nullable=False,
        ),
        sa.Column("orcid_id", sa.String(50), nullable=True),
        sa.Column("affiliation", sa.String(500), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("verification_token", sa.String(255), nullable=True),
        sa.Column("reset_token", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Categories table
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name_uz", sa.String(255), nullable=False),
        sa.Column("name_ru", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    # Volumes table
    op.create_table(
        "volumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_volumes_year", "volumes", ["year"])

    # Issues table
    op.create_table(
        "issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("volume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("cover_image_url", sa.String(1000), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["volume_id"], ["volumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_issues_volume_id", "issues", ["volume_id"])

    # Articles table
    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("abstract", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("keywords", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("submission_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft", "submitted", "under_review", "revision_required",
                "accepted", "rejected", "published", name="articlestatus"
            ),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.Enum("uz", "ru", "en", name="articlelanguage"),
            nullable=False,
        ),
        sa.Column("volume_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pdf_file_path", sa.String(1000), nullable=True),
        sa.Column("pdf_file_size", sa.Integer(), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("search_vector", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.ForeignKeyConstraint(["volume_id"], ["volumes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_articles_doi", "articles", ["doi"], unique=True)
    op.create_index("ix_articles_status", "articles", ["status"])
    op.create_index("ix_articles_author_id", "articles", ["author_id"])
    op.create_index("ix_articles_volume_id", "articles", ["volume_id"])
    op.create_index("ix_articles_issue_id", "articles", ["issue_id"])
    op.create_index("ix_articles_category_id", "articles", ["category_id"])
    op.create_index("ix_articles_status_published", "articles", ["status", "published_date"])

    # Article authors (many-to-many with order)
    op.create_table(
        "article_authors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("guest_name", sa.String(255), nullable=True),
        sa.Column("guest_email", sa.String(255), nullable=True),
        sa.Column("guest_affiliation", sa.String(500), nullable=True),
        sa.Column("guest_orcid", sa.String(50), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_corresponding", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_article_authors_article_id", "article_authors", ["article_id"])

    # Reviews table
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "completed", "declined", name="reviewstatus"),
            nullable=False,
        ),
        sa.Column(
            "recommendation",
            sa.Enum("accept", "minor_revision", "major_revision", "reject", name="reviewrecommendation"),
            nullable=True,
        ),
        sa.Column("comments_to_author", sa.Text(), nullable=True),
        sa.Column("comments_to_editor", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_article_id", "reviews", ["article_id"])
    op.create_index("ix_reviews_reviewer_id", "reviews", ["reviewer_id"])

    # Editorial board members
    op.create_table(
        "editorial_board_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("affiliation", sa.String(500), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "editor_in_chief", "associate_editor", "section_editor", "reviewer",
                name="editorialrole"
            ),
            nullable=False,
        ),
        sa.Column("photo_url", sa.String(1000), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("orcid_id", sa.String(50), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Pages (static CMS content)
    op.create_table(
        "pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("title_uz", sa.String(500), nullable=False),
        sa.Column("title_ru", sa.String(500), nullable=False),
        sa.Column("title_en", sa.String(500), nullable=False),
        sa.Column("content_uz", sa.Text(), nullable=True),
        sa.Column("content_ru", sa.Text(), nullable=True),
        sa.Column("content_en", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("meta_description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pages_slug", "pages", ["slug"], unique=True)

    # Indexing databases
    op.create_table(
        "indexing_databases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("logo_url", sa.String(1000), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Announcements
    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title_uz", sa.String(500), nullable=False),
        sa.Column("title_ru", sa.String(500), nullable=False),
        sa.Column("title_en", sa.String(500), nullable=False),
        sa.Column("content_uz", sa.Text(), nullable=True),
        sa.Column("content_ru", sa.Text(), nullable=True),
        sa.Column("content_en", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("announcements")
    op.drop_table("indexing_databases")
    op.drop_table("pages")
    op.drop_table("editorial_board_members")
    op.drop_table("reviews")
    op.drop_table("article_authors")
    op.drop_table("articles")
    op.drop_table("issues")
    op.drop_table("volumes")
    op.drop_table("categories")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS articlestatus")
    op.execute("DROP TYPE IF EXISTS articlelanguage")
    op.execute("DROP TYPE IF EXISTS reviewstatus")
    op.execute("DROP TYPE IF EXISTS reviewrecommendation")
    op.execute("DROP TYPE IF EXISTS editorialrole")
