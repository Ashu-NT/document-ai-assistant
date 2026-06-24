from __future__ import annotations

from pathlib import Path
from typing import Any

from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.document_chunking_policy import (
    DocumentChunkingPolicy,
)

_CONFIG_DIR = Path("config/chunking")

_PROFILE_FILES: dict[ChunkingProfile, str] = {
    ChunkingProfile.MANUAL: "manual.yaml",
    ChunkingProfile.DATASHEET: "datasheet.yaml",
    ChunkingProfile.CERTIFICATE: "certificate.yaml",
    ChunkingProfile.DRAWING: "drawing.yaml",
    ChunkingProfile.REPORT: "report.yaml",
    ChunkingProfile.DEFAULT: "default.yaml",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return {}
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_policy_from_yaml(
    profile: ChunkingProfile,
    *,
    config_dir: Path | None = None,
) -> DocumentChunkingPolicy | None:
    base = config_dir or _CONFIG_DIR
    filename = _PROFILE_FILES.get(profile)
    if filename is None:
        return None
    data = _load_yaml(base / filename)
    if not data:
        return None
    try:
        return DocumentChunkingPolicy(
            profile_name=profile,
            max_chunk_tokens=int(data["max_chunk_tokens"]),
            chunk_overlap=int(data["chunk_overlap"]),
            same_topic_merge_tokens=int(data["same_topic_merge_tokens"]),
            intro_context_tokens=int(data["intro_context_tokens"]),
            asset_context_window=int(data["asset_context_window"]),
            asset_context_max_tokens=int(data["asset_context_max_tokens"]),
            include_picture_chunks=bool(data.get("include_picture_chunks", True)),
            include_table_context=bool(data.get("include_table_context", True)),
        )
    except (KeyError, TypeError, ValueError):
        return None
