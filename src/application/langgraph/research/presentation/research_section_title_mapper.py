from __future__ import annotations


class ResearchSectionTitleMapper:
    def display_title(self, value: str | None) -> str:
        title = (value or "Section").strip()
        normalized = title.casefold()
        if normalized.startswith("collect "):
            normalized = normalized[8:].strip()
        if "maintenance" in normalized:
            return "Maintenance Findings"
        if "technical specification" in normalized or "technical data" in normalized:
            return "Technical Specifications"
        if "specification" in normalized:
            return "Technical Specifications"
        if "safety" in normalized:
            return "Safety Notes"
        if "procedure" in normalized:
            return "Procedures"
        if "troubleshooting" in normalized:
            return "Troubleshooting Guidance"
        if "comparison" in normalized:
            return "Comparison"
        return title
