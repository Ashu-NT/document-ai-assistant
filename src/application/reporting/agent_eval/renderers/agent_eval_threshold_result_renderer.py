from __future__ import annotations

from typing import Any


class AgentEvalThresholdResultRenderer:
    def render(self, quality_gate_result: Any | None = None) -> list[str]:
        lines = ["", "## Threshold Result", ""]
        if quality_gate_result is None:
            lines.append("Not evaluated.")
        elif getattr(quality_gate_result, "passed", False):
            lines.append("PASS")
        else:
            lines.append("FAIL")
            violations = getattr(quality_gate_result, "violations", [])
            if violations:
                lines.append("")
                for violation in violations:
                    actual = getattr(violation, "actual", None)
                    actual_text = (
                        f"{float(actual):.3f}" if isinstance(actual, int | float) else "n/a"
                    )
                    lines.append(
                        (
                            f"- {violation.metric}: {actual_text} < "
                            f"{violation.threshold:.3f}"
                        )
                    )
        return lines
