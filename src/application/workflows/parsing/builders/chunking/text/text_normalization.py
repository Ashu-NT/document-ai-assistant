import re

def normalize_comparable_text(
    value: str | None,
    *,
    strip_underscores: bool = True,
    casefold: bool = False,
) -> str:
    if not value:
        return ""

    text = value.casefold() if casefold else str(value)
    pattern = r"[\W_]+" if strip_underscores else r"[^\w\s]"
    text = re.sub(pattern, " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text if casefold else text.lower()
