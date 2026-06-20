import re

_TITLE_STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "the",
    "to",
    "with",
}

_GENERIC_SECTION_WORDS = {
    "chapter",
    "section",
    "part",
    "lab",
    "task",
    "prep",
    "exercise",
    "step",
}

_INTRO_MARKERS = {
    "background",
    "familiarize",
    "getting started",
    "introduction",
    "objective",
    "objectives",
    "overview",
    "preparation",
}

_TASK_MARKERS = {
    "calculation",
    "exercise",
    "execution",
    "implementation",
    "instructions",
    "lab task",
    "output",
    "prep task",
    "procedure",
    "reading",
    "setup",
    "step",
    "task",
    "test",
    "testing",
    "verification",
}

_NUMBERING_PREFIX = re.compile(
    r"^(?:chapter|section|part)?\s*\d+(?:\.\d+)*(?:[.)])?\s*",
    re.IGNORECASE,
)
_TASK_PREFIX = re.compile(
    r"^(?:prep|lab)?\s*task\s*\d*(?:[.:)\-])?\s*",
    re.IGNORECASE,
)
_EXERCISE_PREFIX = re.compile(
    r"^(?:exercise|step)\s*\d*(?:[.:)\-])?\s*",
    re.IGNORECASE,
)


def normalize_section_title(title: str | None) -> str:
    if not title:
        return ""

    return re.sub(r"\s+", " ", title).strip().lower()


def semantic_section_title(title: str | None) -> str:
    normalized = normalize_section_title(title)
    if not normalized:
        return ""

    stripped = normalized
    while True:
        updated = _NUMBERING_PREFIX.sub("", stripped, count=1)
        updated = _TASK_PREFIX.sub("", updated, count=1)
        updated = _EXERCISE_PREFIX.sub("", updated, count=1)
        updated = re.sub(r"^[\-\s:.)]+", "", updated).strip()
        if updated == stripped:
            break
        stripped = updated

    return stripped


def section_title_keywords(title: str | None) -> set[str]:
    semantic_title = semantic_section_title(title)
    if not semantic_title:
        return set()

    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_-]*", semantic_title)
        if len(token) > 2
        and token not in _TITLE_STOP_WORDS
        and token not in _GENERIC_SECTION_WORDS
    }


def titles_share_topic(left_title: str | None, right_title: str | None) -> bool:
    left_semantic = semantic_section_title(left_title)
    right_semantic = semantic_section_title(right_title)
    if not left_semantic or not right_semantic:
        return False

    if left_semantic == right_semantic:
        return True

    if left_semantic in right_semantic or right_semantic in left_semantic:
        return True

    return bool(section_title_keywords(left_title) & section_title_keywords(right_title))


def is_introductory_title(title: str | None) -> bool:
    normalized = normalize_section_title(title)
    if not normalized:
        return False

    return any(marker in normalized for marker in _INTRO_MARKERS)


def is_task_like_title(title: str | None) -> bool:
    normalized = normalize_section_title(title)
    if not normalized:
        return False

    if any(marker in normalized for marker in _TASK_MARKERS):
        return True

    return bool(re.match(r"^\d+(?:\.\d+)*(?:[.)])?\s+", normalized))
