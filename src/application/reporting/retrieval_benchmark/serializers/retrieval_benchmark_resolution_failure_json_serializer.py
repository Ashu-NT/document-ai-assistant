from pathlib import Path
from typing import Any


class RetrievalBenchmarkResolutionFailureJsonSerializer:
    def serialize(
        self,
        *,
        details: dict[str, Any] | None,
        subset: str,
        truth_set_path: Path | str,
        manifest_path: Path | str,
    ) -> dict[str, Any]:
        unresolved_case_ids = self._unresolved_case_ids(details)
        return {
            "status": "resolution_failed",
            "subset": subset,
            "truth_set_path": str(truth_set_path),
            "manifest_path": str(manifest_path),
            "unresolved_case_count": len(unresolved_case_ids),
            "unresolved_case_ids": unresolved_case_ids,
            "diagnostics": list((details or {}).get("diagnostics") or []),
        }

    @staticmethod
    def _unresolved_case_ids(details: dict[str, Any] | None) -> list[str]:
        return list((details or {}).get("unresolved_case_ids") or [])
