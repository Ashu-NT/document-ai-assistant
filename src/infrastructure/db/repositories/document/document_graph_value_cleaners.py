from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)


def clean_text(value: object) -> str | None:
    text = repair_docling_text(str(value or "")).strip()
    return text or None


def clean_multiline_text(value: object) -> str | None:
    if value is None:
        return None
    lines = [
        repair_docling_text(str(line)).rstrip()
        for line in str(value).splitlines()
    ]
    text = "\n".join(lines).strip()
    return text or None


def clean_rows(rows: object) -> list[list[str]]:
    if not isinstance(rows, list):
        return []
    cleaned_rows: list[list[str]] = []
    for row in rows:
        if not isinstance(row, list):
            continue
        cleaned_rows.append(
            [
                clean_text(cell) or ""
                for cell in row
            ]
        )
    return cleaned_rows


def clean_parallel_stream_rows(value: object) -> list[list[list[str]]]:
    if not isinstance(value, list):
        return []
    cleaned_streams: list[list[list[str]]] = []
    for stream_rows in value:
        cleaned_rows = clean_rows(stream_rows)
        if cleaned_rows:
            cleaned_streams.append(cleaned_rows)
    return cleaned_streams


def coerce_float(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def clean_header_paths(value: object) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    cleaned_paths: list[list[str]] = []
    for path in value:
        if not isinstance(path, list):
            continue
        cleaned_path = [clean_text(part) or "" for part in path]
        cleaned_path = [part for part in cleaned_path if part]
        cleaned_paths.append(cleaned_path)
    return cleaned_paths


def clean_axis_summary(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    cleaned_summary: dict[str, str] = {}
    for key, raw_value in value.items():
        cleaned_key = clean_text(key)
        cleaned_value = clean_text(raw_value)
        if cleaned_key and cleaned_value:
            cleaned_summary[cleaned_key] = cleaned_value
    return cleaned_summary
