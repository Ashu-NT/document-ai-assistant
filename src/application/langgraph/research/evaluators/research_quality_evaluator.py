from __future__ import annotations


class ResearchQualityEvaluator:
    def evaluate(self, result) -> dict:
        evidence_count = len(result.evidence)
        task_count = len(result.task_results)
        cited_evidence_count = sum(
            1 for item in result.evidence if item.page_start is not None or item.page_end is not None
        )
        return {
            "task_success_rate": (
                sum(1 for task_result in result.task_results if task_result.success) / task_count
                if task_count
                else 0.0
            ),
            "citation_coverage_rate": (
                cited_evidence_count / evidence_count
                if evidence_count
                else 0.0
            ),
            "gap_count": len(result.gaps),
        }
