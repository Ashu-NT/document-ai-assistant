# V7 Retrieval Strategy Fix Audit

## Manual Failures Reviewed

- `AG-012` from `outputs/evaluation/agent/agent_eval_report.{json,md}`
  - Expected `MAINTENANCE_LOOKUP`
  - Observed `PROCEDURE_LOOKUP`
- `AG-024` from `outputs/evaluation/agent/agent_eval_report.{json,md}`
  - Deep research checklist path fails report validation
  - Research report has no sections, so summary/citations/context are not emitted
- `AG-025` from `outputs/evaluation/agent/agent_eval_report.{json,md}`
  - Gap-analysis request returns `0` gaps even though the request explicitly asks for missing evidence

## Current Strategy Flow

1. `AnswerQuestionNode` builds a `RetrievalContext`
2. `RetrievalStrategyService` analyzes the query with `RetrievalQueryAnalyzer`
3. `RetrievalSignalExtractor` converts query/intent/chunk signals into strategy signals
4. `DeterministicStrategySelector` ranks the strategy scores
5. `RetrievalPlanExecutor` runs the selected retrieval plan

## Where Strategy Is Lost In Planned Tasks

- Not the current eval blocker.
- Planned-task strategy aggregation was already wired in prior work and current failures are elsewhere.

## Where Identifier Mutation Happens

- Not the current eval blocker from the latest report.
- The current failing eval set does not show identifier truncation.

## Why Error E12 Becomes PROCEDURE_LOOKUP

- Not currently failing in `run_agent_eval.py`, but the same root area remains the retrieval intent and signal stack under:
  - `src/application/workflows/retrieval/retrieval_query_intent_inferer.py`
  - `src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`
  - `src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py`

## Why Maintenance Intervals Miss TABLE_LOOKUP

- Not currently failing in the full eval report, but the current maintenance classification defect comes from the same selector stack.

## Current Eval Root Causes

### AG-012

- `RetrievalQueryIntentInferer` currently maps generic `maintenance` wording into `PROCEDURE`.
- That intent feeds chunk-type preferences and downstream strategy signals.
- `DeterministicStrategySelector` then ranks `PROCEDURE_LOOKUP` above the expected maintenance path.

### AG-024

- `ChecklistSynthesizer` creates `checklist_items` and references, but no `sections`.
- `ResearchReportBuilder` passes `synthesis.sections` directly into the report.
- `ResearchReportValidator` requires at least one report section.
- Result: the checklist research path fails validation before `ResearchSummaryNode` can emit report-backed context/citations.

### AG-025

- `ResearchGapDetector` only flags:
  - missing required task evidence
  - one-sided comparison evidence
  - too-few sections
  - missing checklist safety evidence
- It does not detect “the retrieved evidence does not actually support the requested missing-evidence claim.”
- Gap-analysis requests can therefore return evidence with `0` gaps even when the request explicitly asks for missing evidence.

## Affected Files

| File | Problem | Fix |
|---|---|---|
| `src/application/workflows/retrieval/retrieval_query_intent_inferer.py` | Maintenance wording collapses into `PROCEDURE` | Split maintenance-summary/interval wording from explicit procedure wording |
| `src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py` | Strategy signals inherit the wrong maintenance/procedure balance | Reinforce maintenance/table/troubleshooting signals after intent correction |
| `src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py` | Final ranking currently accepts the wrong dominant maintenance signal | Keep ranking deterministic but let corrected maintenance signals win cleanly |
| `src/application/langgraph/research/synthesizers/checklist_synthesizer.py` | Checklist synthesis emits no report sections | Build reusable checklist sections from evidence families |
| `src/application/langgraph/research/synthesizers/research_report_builder.py` | Checklist reports depend on empty `sections` | Preserve checklist structure in report sections and markdown |
| `src/application/langgraph/research/evaluators/research_gap_detector.py` | Gap-analysis path does not infer evidence gaps from unsupported claims | Add deterministic missing-evidence heuristics for gap-analysis requests |
| `tests/unit/application/langgraph/...` | Current regressions are not fully covered | Add/update tests for maintenance strategy, checklist report sections, and gap-analysis detection |

## Implementation Plan

1. Fix maintenance intent inference so generic maintenance-task questions resolve to maintenance, not procedure.
2. Keep explicit procedural wording (`how to`, `steps`, `install`, `commission`) on the procedure path.
3. Update retrieval-strategy tests so `AG-012` behavior is directly covered.
4. Refactor checklist synthesis so it emits real report sections plus checklist items and references.
5. Add deterministic gap-analysis heuristics so explicit “missing evidence” requests can produce gaps when evidence is incomplete or weakly aligned.
6. Rerun targeted langgraph tests, then rerun `scripts/run_agent_eval.py` and verify the report improves.
