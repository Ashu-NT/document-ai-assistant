# V8 Deep Research Grounding Failure Audit

## Command Reproduced

```powershell
python scripts/agent_cli.py "Compare maintenance tasks and specifications" --document "FWC12" --deep-research --show-research-plan --show-retrieval-strategy --show-context
```

Observed current runtime defaults during audit:

- `deep_research_enabled=True`
- `llm_research_planning_enabled=True`
- `reflection_enabled=True`
- `retrieval_strategy_enabled=True`
- `llm_retrieval_strategy_enabled=True`
- `enable_answer_generation=True`

Additional controlled probes used to isolate the failure:

1. Deterministic planning + reflection off
2. Deterministic planning + reflection on + generation off
3. Current defaults end to end

## Current Deep Research Flow

Route:

- `route_request` selects `deep_research`
- `find_document` resolves `FWC12`
- `create_research_plan` builds a research plan
- `execute_research` runs task retrieval
- `evaluate_research` optionally adds follow-up tasks
- `synthesize_research` builds `research_synthesis` and `research_report`
- `research_summary` converts the report into `response_text`
- If reflection is enabled, the graph still sends deep research into `reflect_answer`
- `reflect_answer` can send the run into `retry_retrieval`
- `retry_retrieval` uses normal QA regeneration and overwrites `tool_results["answer_question"]`
- `final_response` returns `state.response_text`

Key implementation points:

- [src/application/langgraph/graphs/document_agent_graph.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/graphs/document_agent_graph.py:696) routes deep research through reflection when enabled.
- [src/application/langgraph/nodes/research/research_summary_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/research/research_summary_node.py:61) writes a synthetic `answer_question` payload and marks it as `route="retrieval_qa"`.
- [src/application/langgraph/nodes/question_answering/reflect_answer_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/question_answering/reflect_answer_node.py:50) only checks the payload route, so it treats the research report as standard retrieval QA.
- [src/application/langgraph/nodes/question_answering/retry_retrieval_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/question_answering/retry_retrieval_node.py:175) regenerates through `AnswerQuestionTool`, not through research synthesis.
- [src/application/workflows/question_answering/question_answering_workflow.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/workflows/question_answering/question_answering_workflow.py:216) returns the normal QA disabled-generation message when answer generation is off.
- [src/application/langgraph/nodes/control/final_response_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/control/final_response_node.py:34) returns `state.response_text` only.

## Evidence Found

Stable deterministic baseline:

- Goal type: `comparison`
- Plan tasks:
  - `Collect maintenance tasks`
  - `Collect technical specifications`
- Task result counts:
  - `Collect maintenance tasks`: 8 evidence chunks
  - `Collect technical specifications`: 8 evidence chunks
- Merged research evidence: 14 chunks after global deduplication
- Report sections:
  - `Collect maintenance tasks`
  - `Collect technical specifications`

Representative chunk IDs observed in task results:

- Maintenance task:
  - `chunk_2820a39a4ead45db8898e85fefedc3d4`
  - `chunk_3f7bd1e3fab04446bc0971f68a8ba288`
  - `chunk_229d11432d174622a1b7b18b2418c523`
  - `chunk_868fc4e3fb6a47ae92351fc409bb2bde`
  - `chunk_f57f134b0e664a84bdf112b5978805fd`
- Specification task:
  - `chunk_5651714455624cc788b0dedf0ab68dd5`
  - `chunk_ce5445e3c2804004a7c7b6907f04979b`
  - `chunk_5fc9a9f0b25441f5b2a4ff54a1b4a5de`
  - `chunk_dc3275501dfe4476af7b7a5d2eb5083c`
  - `chunk_bf14faeb7a584f668c3f2605bda38c2a`

Concrete evidence present in retrieved research chunks:

- Page 57 spare parts / part number table
- Page 58 preventive maintenance summary and interval code table
- Pages 59-60 maintenance and cleaning procedures
- Pages 72, 80, 88 technical specification tables
- Page 50 `Press Type / Serial Number / Drive Type / Drive Specification` table

## Where Evidence Is Lost

### 1. Retrieval result -> research task result

Status:

- Preserved

Evidence:

- `ResearchTaskExecutor` converts retrieved chunks into `ResearchEvidence`
- Task-level evidence counts are correct in stable probes

Relevant files:

- [src/application/langgraph/research/executors/research_task_executor.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/executors/research_task_executor.py:73)
- [src/application/langgraph/research/executors/research_executor.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/executors/research_executor.py:43)

### 2. Research task result -> merged research evidence

Status:

- Partially lost

Problem:

- `ResearchEvidenceMerger` deduplicates globally by `chunk_id`
- When the same chunk supports multiple tasks, only one `task_id` survives
- The merger keeps `related_task_ids` only in diagnostics, but later synthesis does not use that field

Impact:

- Comparison evidence can become one-sided after merge
- Follow-up tasks can steal ownership of shared chunks
- A report can collapse to a single section even though multiple task results originally had evidence

Relevant files:

- [src/application/langgraph/research/services/research_evidence_merger.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/services/research_evidence_merger.py:13)
- [src/application/langgraph/research/synthesizers/evidence_synthesizer.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/synthesizers/evidence_synthesizer.py:10)

### 3. Merged evidence -> research synthesis context

Status:

- Usually preserved in the no-reflection baseline
- Unstable when follow-up research is introduced

Problem:

- `EvidenceSynthesizer` groups strictly by `evidence.task_id`
- If merged evidence no longer carries the original task ownership, sections disappear

Observed failure mode:

- Report sections can collapse to `Follow-up research: Comparison evidence is one-sided.` only
- Original `Collect technical specifications` section can vanish despite earlier evidence

Relevant files:

- [src/application/langgraph/research/synthesizers/evidence_synthesizer.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/synthesizers/evidence_synthesizer.py:10)
- [src/application/langgraph/research/evaluators/research_gap_detector.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/evaluators/research_gap_detector.py:36)
- [src/application/langgraph/research/executors/research_iteration_controller.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/research/executors/research_iteration_controller.py:31)

### 4. Research synthesis/report -> answer generation request

Status:

- Lost by design in the current branch

Problem:

- `ResearchSummaryNode` does not return a dedicated research output contract to the downstream graph
- It repackages the research report into a fake `answer_question` tool result with `route="retrieval_qa"`
- That makes reflection and retry logic treat the research report as if it were standard QA output

Relevant files:

- [src/application/langgraph/nodes/research/research_summary_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/research/research_summary_node.py:61)

### 5. Research report -> reflection / retry

Status:

- Major loss point

Problem:

- `ReflectAnswerNode` reviews the research summary because the synthetic payload says `retrieval_qa`
- The reflection prompt is written for “a document-grounded answer”, not for a structured research report
- LLM reflection is enabled by default, so the branch is nondeterministic across identical runs
- If reflection asks for retry, `RetryRetrievalNode` regenerates through `AnswerQuestionTool`
- That discards the research report as the primary response artifact

Observed outcomes:

- Generic fallback: `I could not verify a grounded answer confidently enough from the current evidence.`
- QA disabled message: `I found relevant document evidence, but answer generation is not enabled yet.`
- A normal maintenance QA answer unrelated to the intended comparison structure

Relevant files:

- [src/application/langgraph/reflection/prompts/reflection_prompt_builder.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/reflection/prompts/reflection_prompt_builder.py:68)
- [src/application/langgraph/nodes/question_answering/reflect_answer_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/question_answering/reflect_answer_node.py:78)
- [src/application/langgraph/nodes/question_answering/retry_retrieval_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/question_answering/retry_retrieval_node.py:175)
- [src/application/workflows/question_answering/question_answering_workflow.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/workflows/question_answering/question_answering_workflow.py:216)

### 6. Final response formatting

Status:

- Lost at presentation even when data still exists

Problem:

- `DocumentAgentGraph._build_result()` correctly derives `data["answer"]` from tool payloads
- `FinalResponseNode` and `print_graph_result()` use `state.response_text`
- After reflection failure, `response_text` can be the generic QA fallback even while `data["answer"]` still contains a research report or regenerated QA payload

Relevant files:

- [src/application/langgraph/graphs/document_agent_graph.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/graphs/document_agent_graph.py:367)
- [src/application/langgraph/nodes/control/final_response_node.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/src/application/langgraph/nodes/control/final_response_node.py:34)
- [scripts/agent_cli.py](C:/Users/ashuf/Desktop/Projects/document-ai-assistant/scripts/agent_cli.py:820)

## Why Grounding Fails

The failure is not retrieval.

The actual root causes are:

1. Deep research is being funneled into the normal QA reflection/retry pipeline.
2. The research summary is mislabeled as `retrieval_qa`, so reflection applies the wrong contract.
3. Reflection can retry with a normal QA regeneration path, which overwrites research outputs.
4. `ResearchEvidenceMerger` erases task ownership during chunk deduplication, which can collapse comparison sections or make follow-up evidence dominate.
5. The LLM research planner is enabled by default and the validator only enforces “at least one task”, so comparison plans can degrade to one-sided plans without being rejected.
6. Final CLI output prefers `response_text`, so a late reflection fallback can hide an otherwise valid research report still present in `result.data`.

This maps directly to the likely failure categories from the brief:

- Empty synthesis context:
  - No, not the primary issue
  - Synthesis works in the deterministic no-reflection baseline
- Wrong answer intent:
  - Yes, after retry the system falls back to QA intents like `maintenance_summary`
- Answer generator called with original question instead of research report context:
  - Yes, in `retry_retrieval`
- Research evidence not converted to approved context chunks:
  - The conversion exists, but it is adapted through a QA-shaped payload
- Grounding validator expects QA chunks but receives research objects:
  - Effectively yes, because research is forced through QA reflection semantics
- Task-level answers disabled because generation disabled:
  - Yes, this worsens the failure once retry switches into QA mode
- Final response uses generic QA insufficiency instead of research report:
  - Yes

## Affected Files

| File | Problem | Fix |
|---|---|---|
| `src/application/langgraph/nodes/research/research_summary_node.py` | Converts research report into synthetic `answer_question` payload with `route="retrieval_qa"` | Emit a research-native payload and preserve `research_report` as the primary final artifact |
| `src/application/langgraph/graphs/document_agent_graph.py` | Deep research always goes into reflection when enabled | Add deep-research-specific post-summary branching or route-aware reflection gating |
| `src/application/langgraph/nodes/question_answering/reflect_answer_node.py` | Reviews research output as standard QA and can overwrite it | Skip QA reflection for deep research or add research-aware reflection mode |
| `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py` | Regenerates through `AnswerQuestionTool`, replacing research synthesis | Add research-aware retry/supplement path or block QA retry for deep research |
| `src/application/langgraph/research/services/research_evidence_merger.py` | Dedupes by `chunk_id` and loses task ownership | Preserve evidence per task or dedupe within task families while keeping task links |
| `src/application/langgraph/research/synthesizers/evidence_synthesizer.py` | Groups by `task_id` only, so merged cross-task chunks can disappear from sections | Read task-family membership from merger diagnostics or preserve explicit multi-task attribution |
| `src/application/langgraph/research/evaluators/research_gap_detector.py` | One-sided comparison follow-up is valid, but downstream merging can make it dominate | Keep, but rely on fixed task-aware evidence merge |
| `src/application/langgraph/research/planners/llm_research_planner.py` | LLM plan can under-specify comparison tasks | Add comparison-shape validation before accepting LLM plans |
| `src/application/langgraph/research/validation/research_plan_validator.py` | Accepts any plan with at least one task, even for comparison goals | Require minimum thematic coverage for comparison goals |
| `src/application/workflows/question_answering/question_answering_workflow.py` | QA fallback text leaks into deep research after retry | Prevent deep research from falling back into normal QA generation-disabled messaging |
| `src/application/langgraph/nodes/control/final_response_node.py` | Returns stale `response_text` only | Prefer route-aware answer selection for deep research |
| `scripts/agent_cli.py` | Human output prints `result.response_text`, which can be stale fallback text | For deep research, prefer `result.data["answer"]` or `research_report` over raw `response_text` |

## Implementation Plan

1. Protect deep research from QA reflection fallback.
   - Do not send `route=deep_research` reports through the normal QA reflection contract.
   - Either skip reflection for deep research initially or add a research-specific reflection path that reviews `research_report` directly.

2. Preserve research outputs as first-class final artifacts.
   - Make `research_report` or `research_synthesis` the canonical deep-research answer source.
   - Ensure final response priority for deep research is:
     1. `research_report`
     2. `research_synthesis`
     3. research-specific insufficiency message
     4. never generic QA fallback unless no research evidence exists

3. Stop QA retry from overwriting research state.
   - `retry_retrieval` should not call `AnswerQuestionTool` for deep research.
   - If follow-up retrieval is needed, it should append research evidence and rerun research synthesis.

4. Fix task-aware evidence merging.
   - Preserve task ownership for shared chunks.
   - Support the same chunk contributing to multiple research tasks without collapsing the section structure.
   - Update synthesis to use multi-task attribution safely.

5. Harden comparison-plan acceptance.
   - When `goal_type=comparison`, require at least two comparison topics or equivalent task coverage before accepting an LLM plan.
   - Fall back to deterministic planning if the LLM plan is under-scoped.

6. Fix final presentation.
   - Make `FinalResponseNode` and CLI formatting route-aware.
   - For deep research, prefer the research artifact over stale `response_text`.

7. Add tests.
   - Deep research with evidence returns `research_report`, not QA fallback
   - Reflection does not convert deep research into normal QA retry
   - Shared evidence across tasks preserves both task sections
   - Comparison LLM plans with only one task are rejected or repaired
   - CLI deep research output prefers research answer over stale fallback `response_text`

## Recommendation

Implement fixes in this order:

1. Deep-research final-answer protection
2. Task-aware research evidence merge
3. Comparison-plan validation for LLM research planning
4. CLI / final-response formatting cleanup

That order gives the fastest path from “evidence exists but users see fallback” to stable, correctly structured deep-research output.
