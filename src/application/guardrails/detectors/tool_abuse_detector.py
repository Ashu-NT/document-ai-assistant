from __future__ import annotations

from src.application.guardrails.models.detector_match import DetectorMatch
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity

_TOOL_ABUSE_MARKERS = (
    "powershell",
    "cmd.exe",
    "bash",
    "shell command",
    "execute command",
    "run command",
    "rm -rf",
    "del /s",
    "format c:",
    "python -c",
    "subprocess",
)


class ToolAbuseDetector:
    def detect(self, user_input: str) -> DetectorMatch:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return DetectorMatch(matched=False)
        matched_terms = [marker for marker in _TOOL_ABUSE_MARKERS if marker in normalized]
        if not matched_terms:
            return DetectorMatch(matched=False)
        return DetectorMatch(
            matched=True,
            reason="Request attempts arbitrary command or tool execution outside the document-agent scope.",
            matched_terms=matched_terms,
            severity=GuardrailSeverity.HIGH,
        )
