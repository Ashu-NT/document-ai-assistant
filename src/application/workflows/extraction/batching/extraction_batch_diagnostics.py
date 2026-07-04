from dataclasses import asdict, dataclass
import re


_WINDOWS_PATH_PATTERN = re.compile(r"[A-Za-z]:\\(?:[^\\\r\n]+\\)*[^\\\r\n]+")
_UNIX_PATH_PATTERN = re.compile(r"(?<!\w)/(?:[^/\s]+/)*[^/\s]+")


@dataclass(slots=True)
class ExtractionBatchDiagnostics:
    batch_index: int
    batch_count: int
    chunk_ids: list[str]
    char_count: int
    word_count: int
    model_name: str | None
    parse_success: bool
    parse_error: str | None = None
    raw_response_preview: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def safe_response_preview(response: str, *, max_chars: int) -> str:
    normalized = response.strip().replace("\r\n", "\n")
    normalized = _WINDOWS_PATH_PATTERN.sub("[path]", normalized)
    normalized = _UNIX_PATH_PATTERN.sub("[path]", normalized)
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[:max_chars].rstrip()}..."
