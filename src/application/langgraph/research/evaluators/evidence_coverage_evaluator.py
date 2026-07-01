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
        concept_coverage = self._concept_coverage(result)
        return {
            "task_evidence_counts": task_evidence_counts,
            "page_reference_count": page_reference_count,
            "section_count": section_count,
            "task_success_count": sum(1 for task_result in result.task_results if task_result.success),
            "task_count": len(result.task_results),
            **concept_coverage,
        }

    @staticmethod
    def _concept_coverage(result) -> dict:
        task_result_map = {
            task_result.task_id: task_result
            for task_result in result.task_results
        }
        concepts = [
            str(item).strip()
            for item in list((result.goal.diagnostics or {}).get("concepts", []))
            if str(item).strip()
        ]
        if not concepts:
            return {
                "concept_coverage_ratio": 1.0,
                "covered_concepts": [],
                "uncovered_concepts": [],
            }
        covered: list[str] = []
        uncovered: list[str] = []
        for concept in concepts:
            matched_task = next(
                (
                    task
                    for task in result.plan.tasks
                    if str((task.diagnostics or {}).get("concept") or "").strip().lower()
                    == concept.strip().lower()
                ),
                None,
            )
            if matched_task is None:
                uncovered.append(concept)
                continue
            task_result = task_result_map.get(matched_task.task_id)
            if task_result is not None and task_result.evidence:
                covered.append(concept)
            else:
                uncovered.append(concept)
        ratio = round(len(covered) / len(concepts), 4) if concepts else 1.0
        return {
            "concept_coverage_ratio": ratio,
            "covered_concepts": covered,
            "uncovered_concepts": uncovered,
        }
