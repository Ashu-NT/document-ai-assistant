from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.ingestion.runtime.ingestion_runtime_profile import (
    IngestionRuntimeProfile,
)


@dataclass(slots=True, frozen=True)
class IngestionRuntimeCapabilities:
    requested_profile: IngestionRuntimeProfile
    resolved_profile: IngestionRuntimeProfile
    extraction_enabled: bool
    question_generation_enabled: bool
    deterministic_identifier_scan_enabled: bool
    semantic_linking_enabled: bool

    @property
    def semantic_enrichment_enabled(self) -> bool:
        return self.extraction_enabled or self.semantic_linking_enabled

    def as_diagnostics(self) -> dict[str, object]:
        return {
            "requested_runtime_profile": self.requested_profile.value,
            "ingestion_runtime_profile": self.resolved_profile.value,
            "semantic_enrichment_enabled": self.semantic_enrichment_enabled,
            "extraction_enabled": self.extraction_enabled,
            "question_generation_enabled": self.question_generation_enabled,
            "deterministic_identifier_scan_enabled": (
                self.deterministic_identifier_scan_enabled
            ),
            "semantic_linking_enabled": self.semantic_linking_enabled,
        }
