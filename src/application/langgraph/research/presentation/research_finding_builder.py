from __future__ import annotations

import re
from typing import Any

from src.application.langgraph.research.models import ResearchEvidence
from src.application.langgraph.research.presentation.evidence_finding_extractor import (
    EvidenceFindingExtractor,
)


class ResearchFindingBuilder:
    def __init__(
        self,
        *,
        extractor: EvidenceFindingExtractor | None = None,
    ) -> None:
        self.extractor = extractor or EvidenceFindingExtractor()

    def build_findings(
        self,
        evidence: list[ResearchEvidence],
        *,
        task_title: str | None = None,
        max_findings: int = 5,
    ) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in evidence:
            extracted = self.extractor.extract(
                item,
                task_title=task_title,
                max_findings=max_findings,
            )
            for finding in extracted:
                normalized = self._normalize_finding(finding)
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                findings.append(finding)
                if len(findings) >= max_findings:
                    return findings
        return findings

    @staticmethod
    def _normalize_finding(value: dict[str, Any]) -> str:
        text = str(value.get("text") or "").strip()
        details = value.get("details") or []
        detail_text = " ".join(
            str(item).strip()
            for item in details
            if isinstance(item, str) and item.strip()
        )
        return re.sub(r"[^a-z0-9]+", " ", f"{text} {detail_text}".casefold()).strip()
