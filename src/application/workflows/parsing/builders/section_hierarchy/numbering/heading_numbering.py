import re


_LEADING_NUMBER_PATTERN = re.compile(
    r"^\s*(?P<number>\d+(?:\.\d+)*)\b"
)
_TRAILING_NUMBER_PATTERN = re.compile(
    r"(?P<prefix>.*?\S)\s+(?P<number>\d+\.\d+(?:\.\d+)*)\s*$"
)
_CHAPTER_NUMBER_PATTERN = re.compile(
    r"^\s*(?:chapter|section|part)\s+(?P<number>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)
_TASK_NUMBER_PATTERN = re.compile(
    r"\b(?:task|exercise|step|problem)\s+(?P<number>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)


def extract_heading_number(text: str | None) -> str | None:
    if not text:
        return None

    chapter_match = _CHAPTER_NUMBER_PATTERN.match(text)
    if chapter_match is not None:
        return chapter_match.group("number")

    match = _LEADING_NUMBER_PATTERN.match(text)
    if match is not None:
        return match.group("number")

    trailing_match = _TRAILING_NUMBER_PATTERN.match(text.strip())
    if trailing_match is None:
        return None

    return trailing_match.group("number")


def extract_contextual_number(text: str | None) -> str | None:
    if not text:
        return None

    match = _TASK_NUMBER_PATTERN.search(text)
    if match is None:
        return None

    return match.group("number")


def strip_heading_number(text: str | None) -> str:
    if not text:
        return ""

    stripped = _CHAPTER_NUMBER_PATTERN.sub("", text, count=1).strip()
    if stripped != text.strip():
        return stripped.strip(" .:-")

    match = _LEADING_NUMBER_PATTERN.match(text)
    if match is not None:
        return text[match.end() :].strip(" .:-")

    trailing_match = _TRAILING_NUMBER_PATTERN.match(text.strip())
    if trailing_match is None:
        return text.strip()

    return trailing_match.group("prefix").strip(" .:-")


def numbering_depth(numbering: str | None) -> int | None:
    if not numbering:
        return None

    return len([part for part in numbering.split(".") if part])


def parent_numberings(numbering: str | None) -> list[str]:
    if not numbering:
        return []

    parts = [part for part in numbering.split(".") if part]
    return [".".join(parts[:index]) for index in range(len(parts) - 1, 0, -1)]
