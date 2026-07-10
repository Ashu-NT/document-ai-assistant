import re

# Marker-matching text normalization -- previously reimplemented in
# ChunkSemanticSignalExtractor, family_builder_utils.py, and
# StructuredSectionFragmentBuilder as a byte-identical
# "strip non-alphanumerics (including underscores), collapse whitespace,
# lowercase" helper. TocPageRangeStrategy's copy is a close cousin rather
# than a literal duplicate: it keeps underscores (drops punctuation only)
# and uses str.casefold() instead of str.lower(). The two optional
# parameters below let every call site keep its exact prior behavior
# instead of silently picking one variant for all callers.


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
