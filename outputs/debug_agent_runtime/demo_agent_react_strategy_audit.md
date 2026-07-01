# Demo Agent ReAct + Strategy Audit

## Commands Reproduced

Reproduced locally at component level with:
- `IntentRouter`
- `RetrievalSignalExtractor`
- `DeterministicStrategySelector`
- `DeterministicResearchPlanner`

Current results:

- `troubleshooting procedures and maintenance tasks`
  - route: `answer_question`
  - strategy: `MAINTENANCE_LOOKUP`
  - secondaries: none
  - observed signals: `maintenance`, `procedure`, `troubleshooting`, `compound_query`
  - extra noise: a false specification signal is added because `_SPECIFICATION_TERMS` currently includes `" a"`

- `compare troubleshooting procedures and maintenance tasks`
  - route: `deep_research`
  - strategy: `MAINTENANCE_LOOKUP`
  - secondaries: none
  - research plan tasks: `Collect maintenance tasks` only

- `compare troubleshooting procedures and maintenance`
  - route: `deep_research`
  - strategy: `MAINTENANCE_LOOKUP`
  - secondaries: none
  - research plan tasks: `Collect maintenance tasks` only

## Current Routing Result

- Explicit `compare ... and ...` queries do route to `deep_research`.
- Non-compare multi-intent requests still fall back to `answer_question`.
- Routing is still marker-based and misses important deep-research phrasings such as:
  - `difference between`
  - `contrast`
  - `relationship between`
- The router can detect that a request is compound, but it does not preserve which concepts must remain distinct downstream.

## Current Retrieval Strategy Result

- Signal extraction is still plain substring matching.
- `_SPECIFICATION_TERMS` currently includes `" a"`, which creates false technical-specification signals for ordinary English sentences.
- `compound_query` only contributes `1.0`, so it is too weak to drive multi-strategy selection.
- `MULTI_STRATEGY` is only selected when at least two ranked strategies reach `>= 4.0`.
- In the reproduced queries, `maintenance`, `procedure`, and `troubleshooting` each score `3.0`, so they do not qualify as "strong" and the selector collapses to a single winner.
- Secondary strategies are also filtered by the same `>= 4.0` threshold, so valid related intents disappear.
- Strategy reasons are generic and signal-centric instead of being phrased in terms of the user request.

## Current Deep Research Activation Result

- The compare route activates, so the problem is not initial routing alone.
- Deep research is then narrowed immediately by deterministic planning.
- The comparison planner only knows these families today:
  - maintenance
  - specification
  - safety
  - certificate
- It does not create dedicated comparison tasks for:
  - troubleshooting
  - procedures
  - maintenance tasks as a separate concept from maintenance generally
- It also truncates comparison topics to `topics[:2]`.
- As a result, the reproduced compare requests become a one-task maintenance-only research run even though the route is `deep_research`.

## Current Progress Output Problems

- Progress is timer-driven rather than completion-driven.
- The animation prints one line per tick.
- After it reaches the last stage, it keeps printing that same stage until the work ends.
- This explains repeated lines such as:
  - `Finalizing response...`
  - `Reviewing answer...`
- Deep-research progress is also too coarse. It reports:
  - `Creating research plan`
  - `Executing research tasks`
  - `Merging evidence`
  - `Synthesizing report`
  instead of surfacing real task-level steps like troubleshooting, procedure, and maintenance evidence collection.

## Current ReAct Trace Problems

- Thought summaries are route-generic, not query-aware.
- Deep-research trace output is not rendered as a true research workflow.
- Action rendering is tool-centric and can reduce to lines like:
  - `Tool: answer_question`
- Observation rendering only summarizes merged context chunks or citation counts.
- It does not show task-by-task observations such as:
  - troubleshooting evidence found
  - procedure evidence found
  - maintenance evidence found
- Retrieval strategy rendering for research tasks depends on task hints or shallow heuristics instead of a proper task-by-task explanation.
- Reflection output is simple pass-through text and is not integrated into a professional research trace.

## Current Answer Formatting Problems

- Compare/deep-research answers are still shaped by generic section synthesis rather than a comparison-specific report layout.
- The current comparison synthesizer is narrow and mainly understands maintenance/specification patterns.
- Research report rendering still feels semi-debuggy because findings are followed by separate:
  - `Reference: ...`
  - `Path: ...`
  lines instead of clean inline citations and a compact references block.
- The reference section still prints `Path:` lines, which is not the desired enterprise presentation style.
- The QA answer prompt currently exposes raw internal document identifiers inside the source block:
  - `Document: <title> (<document_id>)`
- That gives the LLM the exact internal ID and can leak it back into the final answer.
- The console presenter prefers `data["answer"]` over `result.response_text`, which can hide a later safe failure message.

## Where Deep Research Is Lost

1. Routing:
   - explicit compare queries can reach `deep_research`
2. Strategy selection:
   - multi-intent evidence is not promoted to `MULTI_STRATEGY`
3. Research planning:
   - troubleshooting and procedures are dropped
   - compare tasks are truncated too aggressively
4. Research execution:
   - task-level strategies, tool names, and evidence counts are captured
   - they are not surfaced well in the demo trace
5. Research summary:
   - deep-research output is flattened into an `answer_question`-shaped payload
6. Reflection:
   - deep-research route skips reflection entirely
7. Final result assembly:
   - QA reflection `FAIL` can be overwritten by stale answer extraction

## Where Strategy Is Too Narrow

- Intent detection is still token-fragile and substring-based.
- Maintenance, procedure, and troubleshooting are not treated as additive by default.
- Table support is not reliably attached when maintenance task / interval / schedule language appears.
- Multi-intent routing and multi-intent retrieval are not aligned:
  - the router can choose `deep_research`
  - the selector can still choose one narrow retrieval strategy
- Strategy reason strings describe internal signal selection rather than user intent.

## Files Affected

| File | Problem | Fix |
|---|---|---|
| `src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py` | Substring matching is noisy; `" a"` creates false specification signals; multi-intent markers are weak and incomplete. | Replace fragile substring detection with word/phrase-aware matching and additive concept extraction for troubleshooting, procedures, maintenance, schedules, and compare-style phrasing. |
| `src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py` | `MULTI_STRATEGY` requires two strategies with score `>= 4.0`, so valid mixed intents collapse to one strategy; secondaries are dropped. | Promote explicit multi-concept requests directly to `MULTI_STRATEGY` and preserve additive secondary strategies without letting one concept suppress another. |
| `src/application/langgraph/routing/intent_router.py` | Deep-research routing is still keyword-fragile and misses phrases like `difference between`, `contrast`, and `relationship between`. | Expand route triggers and make deep-research routing concept-aware rather than depending on a small marker list. |
| `src/application/langgraph/research/planners/deterministic_research_planner.py` | Comparison planning ignores troubleshooting and procedures and truncates topics to two. | Build explicit comparison task families for troubleshooting, procedures, maintenance, and optional table support; remove the `topics[:2]` bottleneck for comparison mode. |
| `src/application/langgraph/nodes/research/execute_research_node.py` | Task-level research trace data exists but is not used effectively by the demo runtime. | Preserve and surface per-task strategies, tool usage, and evidence counts in the trace and progress layers. |
| `src/application/langgraph/nodes/research/research_summary_node.py` | Deep research is flattened into an `answer_question`-shaped payload, which blurs research mode and QA mode. | Preserve research-mode metadata alongside the final answer so the presenter can render a true research workflow. |
| `src/application/agent_runtime/react_loop/react_trace_builder.py` | Trace is generic, tool-centric, and not query/task-aware; deep research can degrade to `Tool: answer_question`. | Render route-aware agent phases: `Understand Request`, `Research Plan`, per-task `Retrieval Strategy`, `Actions & Observations`, and honest `Reflection`. |
| `src/application/agent_runtime/progress/thinking_animation.py` | Prints the last stage repeatedly until completion. | Print each stage once and update long-running stages in-place with elapsed time instead of spamming lines. |
| `src/application/agent_runtime/demo_agent.py` | Progress stages are fixed from input heuristics and do not reflect real research-task execution. | Drive progress from actual route/plan/task lifecycle events instead of a static keyword-based stage list. |
| `src/application/langgraph/nodes/question_answering/reflect_answer_node.py` | Deep-research route skips reflection completely; QA `FAIL` only updates `response_text`. | Decide whether deep research needs a review stage and, for QA `FAIL`, invalidate stale answer payloads so failure remains visible end to end. |
| `src/application/langgraph/common/response_text_resolver.py` | Still prefers the old `answer_question.answer_text` over a later safe failure override. | Respect safe fallback text whenever reflection or guardrails override the generated answer. |
| `src/application/langgraph/graphs/document_agent_graph.py` | `_build_result()` rehydrates stale `answer_question` output into both `data["answer"]` and final `response_text`. | Make result assembly honor safe overrides and preserve research-mode output structure. |
| `src/application/prompts/answer_generation/answer_prompt_builder.py` | Raw prompt sources include internal `document_id`, which can leak into user-facing answers. | Stop exposing internal IDs to the answer-generation model; keep human-readable document titles only. |
| `src/application/langgraph/research/presentation/enterprise_research_report_formatter.py` | Report output still uses debug-like `Reference:` / `Path:` lines rather than polished inline citations and clean references. | Render concise enterprise sections with inline citations and a compact reference list only. |
| `src/application/langgraph/research/presentation/research_executive_summary_builder.py` | Comparison summary is generic and only reasons over the first two sections. | Generate summaries from the full requested topic set and actual evidence coverage. |
| `src/application/langgraph/research/synthesizers/comparison_synthesizer.py` | Comparison logic is narrow and mainly tuned to maintenance/specification output. | Add concept-aware comparison synthesis for troubleshooting, procedures, maintenance, overlaps, and differences. |
| `src/application/agent_runtime/presenters/console_presenter.py` | Final answer rendering prefers stale `data["answer"]`; primary answer rendering is not research-mode aware. | Render from the validated final response and apply route-aware presentation without leaking internal IDs. |
| `tests/unit/application/langgraph/retrieval_strategy/*` | Missing regression coverage for the reproduced multi-intent failures. | Add selector and signal tests for troubleshooting + procedure + maintenance, compare synonyms, and maintenance-table support. |
| `tests/unit/application/langgraph/research/*` | Missing coverage for three-topic compare planning and professional research trace expectations. | Add planner/service/summary tests for troubleshooting, procedures, maintenance, and task-level trace rendering. |
| `tests/unit/application/agent_runtime/*` and `tests/unit/cli_scripts/*` | Missing coverage for progress spam, reflection-fail honesty, doc-id leakage, and research-mode answer formatting. | Add runtime/CLI regression tests around progress, trace quality, failure handling, and no internal-ID leakage. |

## Implementation Plan

1. V8.5 - Guarded LLM Strategy Advisor
   - Introduce a tightly constrained strategy advisor under `src/application/langgraph/strategy_advisor/`.
   - Keep deterministic routing, validation, and execution in control at all times.
   - Require JSON-only strategy-advisor output with whitelisted intents, routes, and strategies.
   - Reject invalid JSON, duplicated concepts, hallucinated tools, concepts not grounded in the user query, and invalid confidence values.
   - Treat the advisor as additive only: deterministic strategies remain; the advisor may add concepts and secondary strategies, never remove them.
   - Upgrade research planning to consume extracted concepts instead of the current hardcoded maintenance/specification families.
   - Add runtime trace events for advisor start, completion, rejection, validation, and strategy merge.
   - Ensure any advisor failure or validation rejection falls back safely to deterministic behavior.

2. V8.6 - Retrieval Strategy Modernization
   - Improve signal extraction so mixed intents are additive instead of winner-take-all.
   - Convert strategy selection into robust multi-strategy retrieval for maintenance, procedures, troubleshooting, and table-backed lookups.
   - Replace generic selector reasons with explanations grounded in the user request.

3. V8.7 - Research Planning & Execution
   - Build dynamic research tasks from extracted concepts instead of a narrow keyword family list.
   - Preserve troubleshooting, procedures, maintenance tasks, tables, overlaps, and differences as distinct research tasks.
   - Surface task-level progress, evidence counts, and strategy usage clearly in research-mode execution.

4. V8.8 - Safe Response Resolution
   - Preserve reflection failures and safe overrides through final result assembly.
   - Remove stale answer resurrection and ensure guarded fallbacks remain visible end to end.

5. V8.9 - Enterprise Presentation
   - Remove internal identifiers from prompts and user-facing output.
   - Upgrade deep-research and comparison answers to polished enterprise report formatting with inline citations and clean references.

6. V8.9.0 - Regression & Evaluation
   - Add regression coverage for routing, advisor validation, concept-driven planning, strategy merging, reflection coverage, and presentation.
   - Benchmark deterministic-only versus guarded LLM-assisted routing/strategy planning for robustness, latency, and fallback safety.

## Live ReAct Streaming Fix Plan

### Problem Summary

Four separate bugs make the demo runtime feel broken during live runs:

| # | Bug | Root cause file | Line(s) |
|---|---|---|---|
| 1 | "Finalizing response..." repeats for the full graph duration | `thinking_animation.py` | 63-65 |
| 2 | Full trace only appears after graph completion | `demo_agent.py` + `react_trace_builder.py` | 132-165, 14-109 |
| 3 | Thought summary is route-generic, ignores actual query | `react_trace_builder.py` | 131-169 |
| 4 | Reflection FAIL is invisible — stale LLM answer shown instead | `console_presenter.py` | 76 |

A fifth problem applies specifically to simple reference lookup queries:

| # | Bug | Root cause file |
|---|---|---|
| 5 | Simple lookup (manufacturer / supplier) gets wrong thought summary | `react_trace_builder.py` |

---

### Bug 1 Fix — Progress Animation Prints Last Stage Once

**File:** `src/application/agent_runtime/progress/thinking_animation.py:63-65`

**Current code:**
```python
if index < len(self.stages) - 1:
    index += 1
else:
    index = len(self.stages) - 1  # stays here and reprints every tick
```

**Fixed code:**
```python
if index < len(self.stages) - 1:
    index += 1
# else: do not increment — hold silently, no reprint
```

After this change, each stage name prints exactly once. When the last stage is reached, the
loop continues sleeping via `self._stop_event.wait(interval_seconds)` but emits no more lines.

---

### Bug 2 Fix — Live Event Streaming Architecture

The graph currently runs via `compiled_graph.invoke()` (blocking). LangGraph also supports
`compiled_graph.stream()`, which yields `(node_name, state_patch)` after each node completes.

**New package:** `src/application/agent_runtime/streaming/`

```
__init__.py
live_agent_event.py      # LiveAgentEvent dataclass + LiveAgentEventType enum
live_event_sink.py       # LiveEventSink protocol + NullEventSink
console_event_sink.py    # ConsoleLiveEventSink — prints events live to stdout
event_stream_adapter.py  # wraps compiled_graph.stream(); maps nodes → events; returns final state
```

**Integration change in `AgentRuntime.run_graph_request()`:**
- Accept optional `event_sink: LiveEventSink | None = None`
- When sink is provided: delegate to `EventStreamAdapter.run_with_streaming(compiled_graph, state)`
- When sink is absent: keep existing `compiled_graph.invoke(state)` call (backwards compatible)

**Integration change in `DemoAgent.execute_graph_command()`:**
- Construct `ConsoleLiveEventSink` (or `NullEventSink` for `--quiet` / `--json`)
- Pass to `runtime.run_graph_request(event_sink=sink)`
- Remove `ProgressIndicator` / `ThinkingAnimation` from this path (or keep only as fallback when
  the graph does not support streaming)

**Node → event mapping:**

| Graph node | Event emitted |
|---|---|
| `route_request` completed | `UNDERSTAND_REQUEST` (route, intent, thought) |
| `retrieve_evidence` start | `ACTION_STARTED` (tool, query) |
| `retrieve_evidence` completed | `ACTION_COMPLETED` (chunk_count) |
| `create_research_plan` start | `PLAN_STARTED` |
| `create_research_plan` completed | `PLAN_COMPLETED` (task_count, tasks) |
| `execute_research` per task | `ACTION_STARTED` → `ACTION_COMPLETED` |
| `reflect_answer` start | `REFLECTION_STARTED` |
| `reflect_answer` completed | `REFLECTION_COMPLETED` (decision, reason) |
| `answer_question` start | `FINAL_STARTED` |
| `final_response` completed | `FINAL_COMPLETED` → `RUN_COMPLETED` |
| `blocked_action` | `BLOCKED` (reason) |
| `error_handler` | `ERROR` (message) |

---

### Bug 3 Fix — Query-Specific Thought Summaries

**File:** `src/application/agent_runtime/react_loop/react_trace_builder.py:131-169`

`build()` already receives `user_input`. Pass it to `_thought_summary()` alongside `data`:

```python
def _thought_summary(
    route: str | None,
    data: dict[str, Any],
    user_input: str,
) -> str:
    intent = (data or {}).get("answer_intent", "")
    if route == "answer_question":
        if intent == "identifier_lookup":
            return "The request asks for specific identifiers; I will retrieve and list exact values from the document."
        if intent == "maintenance_summary":
            return "The request is about maintenance information; I will retrieve relevant tasks and intervals."
        if intent == "procedure_steps":
            return "The request asks for procedural steps; I will retrieve and present them in order."
        if intent == "safety_warnings":
            return "The request is about safety warnings; I will retrieve and present relevant cautions."
        if intent == "troubleshooting":
            return "The request asks for troubleshooting guidance; I will retrieve relevant diagnostic steps."
        return "The request asks for document evidence, so I will retrieve grounded context before answering."
    if route == "deep_research":
        return "The request requires synthesis across multiple evidence groups; I will collect and compare task-specific evidence before writing the report."
    ...  # existing handling for other routes unchanged
```

Update all call sites of `_thought_summary` to pass `user_input`.

---

### Bug 4 Fix — Reflection FAIL Reaches the User

**File:** `src/application/agent_runtime/presenters/console_presenter.py:76`

**Current:**
```python
_console_safe_text((result.data or {}).get("answer") or result.response_text or "")
```

**Fixed:**
```python
_console_safe_text(result.response_text or (result.data or {}).get("answer") or "")
```

`result.response_text` is the graph's final resolved verdict from `final_response_node`. On PASS,
it contains the same answer text. On FAIL, it contains the safe failure message. Preferring it
over `data["answer"]` ensures the verdict is never hidden.

---

### Bug 5 Fix — Reference Lookup Query (No Routing Change Needed)

"manufacturer and supplier page references" routes correctly to `ANSWER_QUESTION` because none
of the `_DEEP_RESEARCH_ROUTE_MARKERS` fire. The fix is entirely in thought summary (Bug 3):
once `_thought_summary` uses `answer_intent`, this query will show intent-specific text.

If the `answer_intent_analyzer` scores it below `IDENTIFIER_LOOKUP`, it may fall to `GENERAL`.
In that case, add "manufacturer" and "supplier" to the `_IDENTIFIER_TERMS` tuple in
`src/application/services/answer_generation/intent/answer_intent_analyzer.py`.

---

### Implementation Sequence

| Step | File | Description |
|---|---|---|
| 1 | `thinking_animation.py:63-65` | Stop reprinting last stage |
| 2 | `console_presenter.py:76` | Prefer `response_text` over stale `data["answer"]` |
| 3 | `react_trace_builder.py:131-169` | Intent-specific thought summaries |
| 4 | `streaming/__init__.py` | Create package |
| 5 | `streaming/live_agent_event.py` | Event value objects |
| 6 | `streaming/live_event_sink.py` | Protocol + NullEventSink |
| 7 | `streaming/console_event_sink.py` | ANSI live output |
| 8 | `streaming/event_stream_adapter.py` | LangGraph stream bridge |
| 9 | `demo_agent_runtime.py` | Accept `event_sink`; use adapter |
| 10 | `demo_agent.py` | Construct sink; pass to runtime |
| 11 | `demo_agent_cli.py` | Thread `--quiet` / `--json` into sink |
| 12 | `tests/unit/application/agent_runtime/streaming/` | Unit tests for all streaming components |
| 13 | `test_live_react_streaming.py` | FAIL visible, PASS shows answer, events in order |
| 14 | `test_reference_lookup_routing.py` | Identifier-lookup thought for manufacturer query |
| 15 | `test_demo_agent_cli_live_output.py` | No duplicate stages; FAIL message reaches CLI |

All tests must pass without Ollama. All LLM-dependent paths use existing mock fixtures.

---

### Acceptance Criteria

- [ ] "Finalizing response..." (or any stage name) appears at most once per query
- [ ] Deep-research stages appear in sequence during graph execution, not only after completion
- [ ] Manufacturer/supplier lookup produces a thought step referencing identifier lookup, not generic boilerplate
- [ ] Reflection FAIL message is visible to the user; pre-reflection LLM answer is not shown
- [ ] All new streaming components have unit tests; no Ollama required
- [ ] No new facade modules or backwards-compatibility shells introduced
