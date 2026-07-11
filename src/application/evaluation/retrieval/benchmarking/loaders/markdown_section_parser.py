import re

_SECTION_PATTERN = re.compile(
    r"^# (?P<number>\d+)\.[^\n]*\n(?P<body>.*?)(?=^# \d+\.|\Z)",
    re.MULTILINE | re.DOTALL,
)


def extract_sections(text: str) -> dict[str, str]:
    return {
        match.group("number"): match.group("body")
        for match in _SECTION_PATTERN.finditer(text)
    }
