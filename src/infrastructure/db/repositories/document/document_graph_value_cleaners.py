from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.domain.assets import FormField, TableParallelStream


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


def clean_parallel_stream_descriptors(value: object) -> list[TableParallelStream]:
    return TableParallelStream.list_from_data(value)


def coerce_float(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def coerce_int(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
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


def clean_form_fields(value: object) -> list[FormField]:
    if not isinstance(value, list):
        return []
    fields: list[FormField] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        key_text = (
            clean_text(entry.get("key_text"))
            if entry.get("key_text") is not None
            else None
        )
        value_text = (
            clean_text(entry.get("value_text"))
            if entry.get("value_text") is not None
            else None
        )
        if not key_text and not value_text:
            continue
        label = (
            clean_text(entry.get("label"))
            if entry.get("label") is not None
            else None
        )
        fields.append(
            FormField(
                label=label,
                key_text=key_text,
                value_text=value_text,
                cell_id=coerce_int(entry.get("cell_id")),
            )
        )
    return fields


def clean_table_signals(value: object) -> frozenset[str]:
    if not isinstance(value, list):
        return frozenset()
    return frozenset(
        cleaned
        for item in value
        if (cleaned := clean_text(item)) is not None
    )
