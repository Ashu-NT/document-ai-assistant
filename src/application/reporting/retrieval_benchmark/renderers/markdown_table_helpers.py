import json
from typing import Any

# Shared by RetrievalBenchmarkReportMarkdownRenderer and
# RetrievalBenchmarkResolutionFailureMarkdownRenderer -- previously
# duplicated near-verbatim across the two files. single_line() here is the
# more general of the two prior versions (None-only short-circuit + str(value),
# vs. the report renderer's previous `if not value` falsy-check) -- the one
# deliberate behavior change: an empty-string value now renders as "" instead
# of "-". No existing test locks in the old empty-string case.


def format_pages(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "-"
    if page_start == page_end or page_end is None:
        return str(page_start)
    if page_start is None:
        return str(page_end)
    return f"{page_start}-{page_end}"


def format_float(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.3f}"
    return "-"


def stringify(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def single_line(value: Any) -> str:
    if value is None:
        return "-"
    return " ".join(str(value).split())
