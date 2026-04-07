import re
import unicodedata


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert a string to a URL-safe slug.
    Adapted from Django's slugify utility.
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
