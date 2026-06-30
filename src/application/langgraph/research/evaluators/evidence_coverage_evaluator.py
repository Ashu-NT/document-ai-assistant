from __future__ import annotations


class EvidenceCoverageEvaluator:
    def evaluate(self, result) -> dict:
        task_evidence_counts = {
            task_result.task_id: len(task_result.evidence)
            for task_result in result.task_results
        }
        page_reference_count = sum(
            1
            for item in result.evidence
            if item.page_start is not None or item.page_end is not None
        )
        section_count = len(
            {
                tuple(item.section_path)
                for item in result.evidence
                if item.section_path
            }
        )
        return {
            "task_evidence_counts": task_evidence_counts,
            "page_reference_count": page_reference_count,
            "section_count": section_count,
            "task_success_count": sum(1 for task_result in result.task_results if task_result.success),
            "task_count": len(result.task_results),
        }
