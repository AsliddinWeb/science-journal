"""CSV export service for admin panel."""
import csv
import io
from typing import Any


def export_articles_csv(articles: list[Any]) -> bytes:
    """Export articles list to CSV bytes (UTF-8 BOM for Excel compatibility)."""
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        "ID", "Title (EN)", "Title (UZ)", "Title (RU)",
        "Authors", "Category", "Volume", "Issue",
        "DOI", "Language", "Submitted Date", "Published Date",
        "Status", "Downloads", "Views",
    ]
    writer.writerow(headers)

    for article in articles:
        title = article.title if isinstance(article.title, dict) else {}
        title_en = title.get("en", "")
        title_uz = title.get("uz", "")
        title_ru = title.get("ru", "")

        authors: list[str] = []
        if article.author:
            authors.append(article.author.full_name)
        for ca in getattr(article, "co_authors", []):
            if ca.user:
                authors.append(ca.user.full_name)
            elif ca.guest_name:
                authors.append(ca.guest_name)

        category_name = ""
        if article.category:
            cat = article.category
            category_name = getattr(cat, "name_en", "") or getattr(cat, "name_uz", "")

        volume_num = article.volume.number if article.volume else ""
        issue_num = article.issue.number if article.issue else ""

        submitted = (
            article.submission_date.strftime("%Y-%m-%d")
            if article.submission_date
            else ""
        )
        published = (
            article.published_date.strftime("%Y-%m-%d")
            if article.published_date
            else ""
        )

        writer.writerow([
            str(article.id),
            title_en,
            title_uz,
            title_ru,
            "; ".join(authors),
            category_name,
            volume_num,
            issue_num,
            article.doi or "",
            article.language.value if hasattr(article.language, "value") else article.language,
            submitted,
            published,
            article.status.value if hasattr(article.status, "value") else article.status,
            article.download_count,
            article.view_count,
        ])

    return output.getvalue().encode("utf-8-sig")
