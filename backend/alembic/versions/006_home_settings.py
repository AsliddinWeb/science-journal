"""Add home_settings table

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE home_settings (
            id VARCHAR(50) PRIMARY KEY DEFAULT 'default',
            hero_title JSONB NOT NULL DEFAULT '{}'::jsonb,
            hero_subtitle JSONB NOT NULL DEFAULT '{}'::jsonb,
            hero_issn VARCHAR(100),
            about_title JSONB NOT NULL DEFAULT '{}'::jsonb,
            about_text JSONB NOT NULL DEFAULT '{}'::jsonb,
            about_image_url VARCHAR(1000),
            issn_online VARCHAR(50),
            issn_print VARCHAR(50),
            license_type VARCHAR(100),
            announcement_uz TEXT,
            announcement_ru TEXT,
            announcement_en TEXT,
            announcement_active BOOLEAN NOT NULL DEFAULT false,
            cta_title JSONB NOT NULL DEFAULT '{}'::jsonb,
            cta_subtitle JSONB NOT NULL DEFAULT '{}'::jsonb,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # Insert default row
    op.execute("""
        INSERT INTO home_settings (id, hero_title, hero_subtitle, hero_issn, about_title, about_text, issn_online, license_type, cta_title, cta_subtitle)
        VALUES (
            'default',
            '{"uz": "Fan va Innovatsiya", "ru": "Наука и Инновации", "en": "Science and Innovation"}'::jsonb,
            '{"uz": "Fan, texnologiya va innovatsiya sohalari bo''yicha ilg''or tadqiqotlarni nashr etuvchi peer-review ochiq manbali jurnal.", "ru": "Рецензируемый журнал открытого доступа, публикующий передовые исследования.", "en": "A peer-reviewed open access journal publishing cutting-edge research across science, technology, and innovation."}'::jsonb,
            'ISSN: 2181-0842',
            '{"uz": "Jurnal haqida", "ru": "О журнале", "en": "About the Journal"}'::jsonb,
            '{"uz": "", "ru": "", "en": ""}'::jsonb,
            '2181-0842',
            'CC BY 4.0',
            '{"uz": "Tadqiqotingizni nashr etishga tayyormisiz?", "ru": "Готовы опубликовать исследование?", "en": "Ready to publish your research?"}'::jsonb,
            '{"uz": "Jurnalimizda maqola chop ettirgan minglab tadqiqotchilarga qo''shiling.", "ru": "Присоединяйтесь к тысячам исследователей.", "en": "Join thousands of researchers who have published with us."}'::jsonb
        )
    """)


def downgrade() -> None:
    op.drop_table('home_settings')
