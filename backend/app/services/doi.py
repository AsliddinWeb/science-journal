import re
from typing import Optional


def validate_doi(doi: str) -> bool:
    """Validate DOI format (10.XXXX/XXXXX)."""
    pattern = r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$"
    return bool(re.match(pattern, doi, re.IGNORECASE))


def format_doi_url(doi: str) -> str:
    """Return the full DOI resolver URL."""
    clean_doi = doi.strip().lstrip("https://doi.org/").lstrip("http://dx.doi.org/")
    return f"https://doi.org/{clean_doi}"


def generate_journal_doi(volume: int, issue: int, article_number: int, prefix: str = "10.5281") -> str:
    """
    Generate a DOI for an article.
    Format: 10.XXXXX/journal.v{volume}i{issue}.{article_number}
    """
    return f"{prefix}/journal.v{volume}i{issue}.{article_number}"
