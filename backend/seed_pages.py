"""
Run once to seed static pages into the database:
    python seed_pages.py
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.page import Page

PAGES = [
    {
        "slug": "about",
        "title_uz": "Jurnal haqida",
        "title_ru": "О журнале",
        "title_en": "About the Journal",
        "content_uz": "## Jurnal haqida\n\nFan va Innovatsiya jurnali...",
        "content_ru": "## О журнале\n\nЖурнал Science and Innovation...",
        "content_en": "## About the Journal\n\nScience and Innovation Journal...",
    },
    {
        "slug": "aims",
        "title_uz": "Maqsad va doiraviy",
        "title_ru": "Цели и охват",
        "title_en": "Aims & Scope",
        "content_uz": "## Maqsad va doiraviy\n\nJurnal maqsadi...",
        "content_ru": "## Цели и охват\n\nЦель журнала...",
        "content_en": "## Aims & Scope\n\nThe journal aims to...",
    },
    {
        "slug": "author-guidelines",
        "title_uz": "Muallif ko'rsatmalari",
        "title_ru": "Руководство для авторов",
        "title_en": "Author Guidelines",
        "content_uz": "## Muallif ko'rsatmalari\n\nMaqola yuborish uchun...",
        "content_ru": "## Руководство для авторов\n\nДля подачи статьи...",
        "content_en": "## Author Guidelines\n\nTo submit an article...",
    },
    {
        "slug": "review-process",
        "title_uz": "Ko'rib chiqish jarayoni",
        "title_ru": "Процесс рецензирования",
        "title_en": "Review Process",
        "content_uz": "## Ko'rib chiqish jarayoni\n\nIkki tomonlama ko'r-ko'rona baholash...",
        "content_ru": "## Процесс рецензирования\n\nДвойное слепое рецензирование...",
        "content_en": "## Review Process\n\nDouble-blind peer review...",
    },
    {
        "slug": "open-access",
        "title_uz": "Ochiq kirish siyosati",
        "title_ru": "Политика открытого доступа",
        "title_en": "Open Access Policy",
        "content_uz": "## Ochiq kirish siyosati\n\nBarcha maqolalar bepul...",
        "content_ru": "## Политика открытого доступа\n\nВсе статьи находятся в открытом доступе...",
        "content_en": "## Open Access Policy\n\nAll articles are freely available...",
    },
    {
        "slug": "plagiarism",
        "title_uz": "Plagiat siyosati",
        "title_ru": "Политика плагиата",
        "title_en": "Plagiarism Policy",
        "content_uz": "## Plagiat siyosati\n\nJurnal plagiatga qarshi...",
        "content_ru": "## Политика плагиата\n\nЖурнал применяет строгую политику...",
        "content_en": "## Plagiarism Policy\n\nThe journal applies strict anti-plagiarism...",
    },
    {
        "slug": "indexing",
        "title_uz": "Indekslash",
        "title_ru": "Индексирование",
        "title_en": "Indexing",
        "content_uz": "## Indekslash\n\nJurnal quyidagi bazalarda indekslangan...",
        "content_ru": "## Индексирование\n\nЖурнал индексируется в следующих базах...",
        "content_en": "## Indexing\n\nThe journal is indexed in the following databases...",
    },
    {
        "slug": "privacy",
        "title_uz": "Maxfiylik siyosati",
        "title_ru": "Политика конфиденциальности",
        "title_en": "Privacy Policy",
        "content_uz": "## Maxfiylik siyosati\n\n...",
        "content_ru": "## Политика конфиденциальности\n\n...",
        "content_en": "## Privacy Policy\n\n...",
    },
    {
        "slug": "terms",
        "title_uz": "Foydalanish shartlari",
        "title_ru": "Условия использования",
        "title_en": "Terms of Use",
        "content_uz": "## Foydalanish shartlari\n\n...",
        "content_ru": "## Условия использования\n\n...",
        "content_en": "## Terms of Use\n\n...",
    },
    {
        "slug": "license-agreement",
        "title_uz": "Litsenziya shartnomasi",
        "title_ru": "Лицензионное соглашение",
        "title_en": "License Agreement",
        "content_uz": "## Litsenziya shartnomasi\n\nCC BY 4.0...",
        "content_ru": "## Лицензионное соглашение\n\nCC BY 4.0...",
        "content_en": "## License Agreement\n\nCC BY 4.0...",
    },
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            for data in PAGES:
                existing = await session.execute(
                    select(Page).where(Page.slug == data["slug"])
                )
                if existing.scalar_one_or_none():
                    print(f"  skip  /pages/{data['slug']} (already exists)")
                    continue

                page = Page(
                    id=uuid.uuid4(),
                    is_published=True,
                    meta_description=None,
                    **data,
                )
                session.add(page)
                print(f"  create /pages/{data['slug']}")

    await engine.dispose()
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(seed())
