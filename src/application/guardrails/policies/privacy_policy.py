from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PrivacyPolicy:
    redact_internal_ids: bool = True
    redact_file_paths: bool = True
    redact_prompt_markers: bool = True
    redact_secret_like_values: bool = True
