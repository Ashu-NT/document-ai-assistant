from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.validation.document_quality import DocumentQualityResult


class QualityResultSerializer:
    """Serializes already-computed DocumentQualityResult objects into a
    report payload. Does not run any quality checks itself -- the caller
    (ParsingWorkflow) owns invoking DocumentQualityGate and passes the
    results in, so this module has no dependency on the validation layer.
    """

    def serialize(
        self,
        document_id: str,
        *,
        parse_result: DocumentQualityResult,
        chunk_result: DocumentQualityResult,
    ) -> dict[str, object]:
        return {
            "document_id": document_id,
            "parsing": self._serialize_result(parse_result),
            "chunking": self._serialize_result(chunk_result),
            "overall_passed": parse_result.passed and chunk_result.passed,
        }

    @staticmethod
    def _serialize_result(result: DocumentQualityResult) -> dict[str, object]:
        return {
            "passed": result.passed,
            "summary": result.summary(),
            "checks": [
                {
                    "name": check.check_name,
                    "passed": check.passed,
                    "severity": check.severity,
                    "message": check.message,
                    "details": check.details,
                }
                for check in result.checks
            ],
        }
