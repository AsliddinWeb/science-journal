"""
Seed default article categories. Idempotent — existing slugs are skipped.

    python seed_categories.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.category import Category

CATEGORIES = [
    {
        "slug": "natural-sciences",
        "name_uz": "Tabiiy fanlar",
        "name_ru": "Естественные науки",
        "name_en": "Natural Sciences",
        "order": 1,
    },
    {
        "slug": "technical-sciences",
        "name_uz": "Texnik fanlar",
        "name_ru": "Технические науки",
        "name_en": "Technical Sciences",
        "order": 2,
    },
    {
        "slug": "medical-sciences",
        "name_uz": "Tibbiyot fanlari",
        "name_ru": "Медицинские науки",
        "name_en": "Medical Sciences",
        "order": 3,
    },
    {
        "slug": "social-sciences",
        "name_uz": "Ijtimoiy fanlar",
        "name_ru": "Социальные науки",
        "name_en": "Social Sciences",
        "order": 4,
    },
    {
        "slug": "humanities",
        "name_uz": "Gumanitar fanlar",
        "name_ru": "Гуманитарные науки",
        "name_en": "Humanities",
        "order": 5,
    },
    {
        "slug": "economics",
        "name_uz": "Iqtisod fanlari",
        "name_ru": "Экономические науки",
        "name_en": "Economics",
        "order": 6,
    },
    {
        "slug": "education",
        "name_uz": "Pedagogika",
        "name_ru": "Педагогика",
        "name_en": "Education",
        "order": 7,
    },
    {
        "slug": "computer-science",
        "name_uz": "Informatika",
        "name_ru": "Информатика",
        "name_en": "Computer Science",
        "order": 8,
    },
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    created = 0
    skipped = 0
    async with Session() as db:
        async with db.begin():
            for data in CATEGORIES:
                existing = await db.execute(
                    select(Category).where(Category.slug == data["slug"])
                )
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue
                db.add(Category(**data))
                created += 1

    await engine.dispose()
    print(f"Categories seed: created={created}, skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
