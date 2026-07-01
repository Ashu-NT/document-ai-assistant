# Live ReAct Streaming Audit

**Date:** 2026-07-01  
**Scope:** Demo agent runtime — progress display, trace rendering, intent routing, reflection failure handling  
**Status:** Audit only. No implementation changes made.

---

## 1. Root Cause: Repeated "Finalizing response..."

**File:** `src/application/agent_runtime/progress/thinking_animation.py:53-65`

```python
def _run(self) -> None:
    index = 0
    while not self._stop_event.is_set():
        self._last_stage = self.stages[min(index, len(self.stages) - 1)]
        print(f"{self._last_stage}...", file=self.stream, flush=True)
        if self._stop_event.wait(self.interval_seconds):
            return
        if index < len(self.stages) - 1:
            index += 1
        else:
            index = len(self.stages) - 1  # ← clamps here and reprints every tick
```

Once `index` reaches the last stage, it is set back to `len(self.stages) - 1` on every loop
iteration. The while-loop continues until the stop event fires. With `interval_seconds=1.0`
(the default) and a graph that takes 8–15 seconds on deep research, the last stage name
prints 8–15 times. On slow hardware or when LLM latency is high, the user sees:

```
Finalizing response...
Finalizing response...
Finalizing response...
Finalizing response...
```

**Fix required:** Each stage should print exactly once. The final stage should print once and
then either hold silently or update elapsed time in-place (via carriage return / ANSI).

---

## 2. Root Cause: Trace Only Appears After Full Graph Completion

**Files:**
- `src/application/agent_runtime/demo_agent.py:132-165`
- `src/application/agent_runtime/progress/progress_indicator.py:23-41`
- `src/application/agent_runtime/react_loop/react_trace_builder.py:14-109`
- `scripts/demo_agent_cli.py:169-235`

**Execution sequence (all synchronous, single-thread):**

```
demo_agent_cli.py
  └─ demo_agent.process_input(user_input)          # line 169
       └─ demo_agent.execute_graph_command()        # demo_agent.py:132
            ├─ progress_indicator.run_with_progress(stages, _invoke)  # line 154
            │    ├─ ThinkingAnimation.start()       # thread spawned
            │    ├─ _invoke()  →  runtime.run_graph_request()         # BLOCKS
            │    │    └─ document_agent_graph.run() →  _invoke(state) # LangGraph
            │    │         └─ compiled_graph.invoke(initial_state)    # BLOCKS until all nodes done
            │    └─ ThinkingAnimation.stop()
            ├─ react_trace = trace_builder.build(result=result)       # AFTER graph
            └─ session_manager.update_from_graph_result(...)
  └─ _print_handled_result(result, session)          # line 201
       └─ console_presenter.render_graph_result(...)  # prints trace + answer together
```

The graph executes via `compiled_graph.invoke()` which is a blocking LangGraph call. There is
no streaming, no node callback, no event bus. The animation thread runs in parallel but only
shows static stage names — it has no awareness of which graph node is actually executing.

`ReactTraceBuilder.build()` is called only after `run_graph_request()` returns the full
`GraphResult`. It reads `result.data` and `result.route` to reconstruct what happened. The
trace is never emitted incrementally.

`_print_handled_result` in the CLI is called only after `process_input()` returns — which is
only after both graph execution and trace building are complete.

**The result:** A user asking a deep-research question sees the animation for 10–30 seconds,
then the full trace appears all at once with no intermediate feedback.

---

## 3. Root Cause: Generic Thought Summary (Not Query-Specific)

**File:** `src/application/agent_runtime/react_loop/react_trace_builder.py:131-169`

```python
def _thought_summary(route: str | None, data: dict[str, Any]) -> str:
    if route == "answer_question":
        return "The request asks for document evidence, so I will retrieve grounded context before answering."
    if route == "planned_task":
        return "The request has multiple parts, so I will execute a validated plan step by step."
    if route == "deep_research":
        return "The request requires synthesis across evidence groups, so I will collect task-specific evidence before writing the report."
    ...
```

This function receives `user_input` indirectly (via `data`) but does not use it. Every
`answer_question` query — whether the user asked for "manufacturer page references" or
"torque specs for the main shaft" — produces the identical summary.

`data` contains `answer_intent` (e.g. `"identifier_lookup"`, `"maintenance_summary"`) and the
actual query string is available to the caller. Neither is consulted.

**Impact:** The ReAct trace's first Thought step is always a route-based boilerplate, giving
the impression the agent did not understand the specific request.

---

## 4. Root Cause: Reflection FAIL Does Not Suppress Stale Answer

**Files:**
- `src/application/langgraph/nodes/question_answering/reflect_answer_node.py:189-192`
- `src/application/agent_runtime/presenters/console_presenter.py:76`
- `src/application/langgraph/graphs/document_agent_graph.py:376-479`

**What happens on FAIL:**

`reflect_answer_node.py` returns:
```python
if decision == "FAIL":
    return {
        "response_text": REFLECTION_SAFE_FAILURE_MESSAGE,
    }
```

Only `response_text` is patched. The graph state key `tool_results["answer_question"]["data"]["answer"]`
is never cleared. `document_agent_graph._build_result()` assembles `GraphResult.data` from
`tool_results`, so `result.data["answer"]` still holds the pre-reflection generated answer.

`console_presenter.render_graph_result()` at line 76:
```python
_console_safe_text((result.data or {}).get("answer") or result.response_text or "")
```

`result.data["answer"]` is non-empty (the LLM-generated answer), so Python's `or` short-circuits
and `result.response_text` (the safe failure message) is never shown.

**The result:** A reflection FAIL is invisible. The user sees a confident LLM answer that the
reflection subsystem determined was not sufficiently grounded.

---

## 5. Root Cause: Simple Reference Lookup Gets Wrong Thought Summary

**Query example:** "what are the manufacturer and supplier page references"

**File:** `src/application/langgraph/routing/intent_router.py:512-524`

The deep-research markers are:
```
"compare", "analyze", "research", "report", "checklist", "summarize all",
"find every", "identify missing", "cross-check", "across the document",
"all maintenance", "all inspection", "all warnings", "all specifications",
"preventive maintenance", "evidence supports"
```

"manufacturer", "supplier", and "page references" do not match any marker. The query routes
correctly to `ANSWER_QUESTION`. The `answer_intent_analyzer` scores it toward
`IDENTIFIER_LOOKUP` (matching terms: "manufacturer", "supplier" are close enough; if the
source blocks contain part number / model / order code language, the score rises further).

But `_thought_summary("answer_question", data)` ignores `data["answer_intent"]` and returns
the same boilerplate for every answer_question route, regardless of whether the intent was
`IDENTIFIER_LOOKUP`, `MAINTENANCE_SUMMARY`, or `GENERAL`.

**The result:** "The request asks for document evidence, so I will retrieve grounded context
before answering." — which is technically accurate but communicates nothing specific to the user.

---

## 6. Root Cause: Progress Stages Not Tied to Actual Execution

**File:** `src/application/agent_runtime/demo_agent.py:226-258`

```python
def _progress_stages(user_input: str, runtime_options) -> list[str]:
    if _is_deep_research(user_input, runtime_options):
        return [
            "Creating research plan",
            "Executing research tasks",
            "Merging evidence",
            "Synthesizing report",
        ]
    return [
        "Routing request",
        "Selecting retrieval strategy",
        "Retrieving evidence",
        "Generating grounded answer",
        "Finalizing response",
    ]
```

Stage names are determined from a keyword heuristic on `user_input` before the graph runs.
They are passed to `ThinkingAnimation`, which advances through them on a fixed timer — one per
`interval_seconds`. If the graph finishes fast, stages are skipped; if slow, the last one
repeats. There is no connection between which LangGraph node is executing and which stage
name the user sees.

---

## 7. Proposed Streaming Architecture

The goal is to emit events from graph nodes as they execute and display them live on the
console, replacing the static timer-driven animation.

### 7.1 Package Layout

```
src/application/agent_runtime/streaming/
    __init__.py
    live_agent_event.py      # event value objects (dataclasses)
    live_event_sink.py       # LiveEventSink protocol + NullEventSink
    console_event_sink.py    # ANSI terminal output
    event_stream_adapter.py  # bridges LangGraph stream → sink
```

### 7.2 Event Catalogue

| Event constant | When emitted | Key payload fields |
|---|---|---|
| `RUN_STARTED` | Before graph invoke | `query`, `route_hint` |
| `UNDERSTAND_REQUEST` | After routing node completes | `route`, `intent`, `thought` |
| `STRATEGY_STARTED` | Before strategy selection | |
| `STRATEGY_COMPLETED` | After strategy selection | `strategy`, `reason` |
| `PLAN_STARTED` | Before plan creation | |
| `PLAN_COMPLETED` | After plan creation | `task_count`, `tasks` |
| `ACTION_STARTED` | Before each retrieval / tool call | `tool`, `query` |
| `ACTION_COMPLETED` | After each retrieval / tool call | `chunk_count` |
| `OBSERVATION` | Evidence available | `summary`, `source_count` |
| `REFLECTION_STARTED` | Before reflection review | |
| `REFLECTION_COMPLETED` | After reflection review | `decision`, `reason` |
| `FINAL_STARTED` | Before answer generation | |
| `FINAL_COMPLETED` | After answer generation | |
| `RUN_COMPLETED` | After full graph returns | `elapsed_ms` |
| `ERROR` | On unhandled exception | `message` |
| `BLOCKED` | On safety/scope block | `reason` |

### 7.3 LiveEventSink Interface

```python
# live_event_sink.py
from __future__ import annotations
from typing import Protocol
from src.application.agent_runtime.streaming.live_agent_event import LiveAgentEvent

class LiveEventSink(Protocol):
    def emit(self, event: LiveAgentEvent) -> None: ...

class NullEventSink:
    def emit(self, event: LiveAgentEvent) -> None:
        pass
```

### 7.4 ConsoleLiveEventSink Behavior

- Prints each event on a new line with a prefix character (e.g. `·`, `→`, `✓`)
- For `ACTION_STARTED` / `ACTION_COMPLETED`, prints inline with elapsed time
- Does not reprint lines; does not use `\r` overwrite (keeps log scrollable)
- Respects `quiet` flag (no output) and `json` flag (emits JSON lines instead)

### 7.5 EventStreamAdapter

LangGraph supports `compiled_graph.stream(initial_state)` which yields `(node_name, state_patch)`
tuples as each node completes. The adapter wraps this:

```python
# event_stream_adapter.py
class EventStreamAdapter:
    def __init__(self, sink: LiveEventSink): ...

    def run_with_streaming(self, compiled_graph, initial_state) -> AgentState:
        final_state = {}
        for node_name, patch in compiled_graph.stream(initial_state):
            event = self._map_node_to_event(node_name, patch)
            if event is not None:
                self.sink.emit(event)
            final_state.update(patch)
        return final_state
```

Node → event mapping:

| LangGraph node | Events emitted |
|---|---|
| `route_request` | `UNDERSTAND_REQUEST` |
| `retrieve_evidence` | `ACTION_STARTED` → `ACTION_COMPLETED` |
| `answer_question` | `FINAL_STARTED` |
| `reflect_answer` | `REFLECTION_STARTED` → `REFLECTION_COMPLETED` |
| `final_response` | `FINAL_COMPLETED` → `RUN_COMPLETED` |
| `create_research_plan` | `PLAN_STARTED` → `PLAN_COMPLETED` |
| `execute_research` | `ACTION_STARTED` → `ACTION_COMPLETED` (per task) |
| `synthesize_research` | `OBSERVATION` |
| `blocked_action` | `BLOCKED` |
| `error_handler` | `ERROR` |

### 7.6 Integration in DemoAgent

`execute_graph_command` currently calls:
```python
result = self.progress_indicator.run_with_progress(stages, _invoke)
```

After the fix it should:
1. Construct a `ConsoleLiveEventSink` (or `NullEventSink` for `--quiet`/`--json`)
2. Pass it to `AgentRuntime.run_graph_request(event_sink=sink)`
3. Remove `ProgressIndicator` entirely (or keep as a fallback for non-streaming mode)
4. The sink emits each event live; no thread, no timer, no repeated last stage

### 7.7 ThinkingAnimation Fix (Minimal — Applied Regardless of Streaming)

Even without the full streaming architecture, the current `_run()` spam is fixable by a
one-line change in `thinking_animation.py:63-65`:

**Current (reprints last stage):**
```python
else:
    index = len(self.stages) - 1
```

**Fixed (prints each stage once, then stops advancing):**
```python
# do not increment — hold silently after last stage
```

The loop still sleeps via `self._stop_event.wait(self.interval_seconds)`, so no busy-spin.
It just stops printing new lines after all stages have been shown once.

---

## 8. Reflection FAIL Fix

**File:** `src/application/agent_runtime/presenters/console_presenter.py:76`

Current:
```python
_console_safe_text((result.data or {}).get("answer") or result.response_text or "")
```

Fixed (prefer `response_text` if set, fall back to `data["answer"]` only when it is absent):
```python
_console_safe_text(result.response_text or (result.data or {}).get("answer") or "")
```

This works because:
- On PASS / no reflection: `response_text` contains the same answer as `data["answer"]`
- On FAIL: `response_text` is the safe failure message (non-empty), takes precedence
- On CLARIFY: `response_text` is the clarification prompt, takes precedence

The rule is: `response_text` is the graph's final verdict; `data["answer"]` is the pre-verdict
LLM output. The final verdict always wins.

---

## 9. Query-Specific Thought Summary Fix

**File:** `src/application/agent_runtime/react_loop/react_trace_builder.py:131-169`

The `build()` method already receives `user_input` as a parameter (line 14). Pass it through
to `_thought_summary`:

```python
def _thought_summary(route: str | None, data: dict[str, Any], user_input: str) -> str:
    intent = (data or {}).get("answer_intent", "")
    # intent-specific summaries for answer_question route
    if route == "answer_question":
        if intent == "identifier_lookup":
            return f"The request asks for specific identifiers; I will retrieve and list exact values from the document."
        if intent == "maintenance_summary":
            return f"The request is about maintenance information; I will retrieve relevant tasks and intervals."
        if intent == "procedure_steps":
            return f"The request asks for procedural steps; I will retrieve and present them in order."
        return "The request asks for document evidence, so I will retrieve grounded context before answering."
    if route == "deep_research":
        # extract two or three key nouns from user_input for specificity
        ...
```

---

## 10. Implementation Order

This is the recommended sequence to minimize conflicts and allow incremental testing:

1. **Fix `thinking_animation.py`** — print each stage once, no repeat. One-line change.
   Tests: `test_demo_agent_cli_live_output.py` — assert no duplicate stage lines.

2. **Fix `console_presenter.py:76`** — prefer `response_text` over stale `data["answer"]`.
   Tests: `test_live_react_streaming.py` — assert FAIL message is displayed; assert PASS shows answer.

3. **Fix `react_trace_builder._thought_summary()`** — pass `user_input` and `answer_intent`; emit
   intent-specific summaries.
   Tests: `test_reference_lookup_routing.py` — assert thought summary mentions identifiers.

4. **Create `src/application/agent_runtime/streaming/` package** — events, sink interface, null sink.
   No tests needed beyond import smoke test.

5. **Create `console_event_sink.py`** — live ANSI output.
   Tests: capture stdout and assert events appear in emission order.

6. **Create `event_stream_adapter.py`** — bridge LangGraph stream to sink.
   Tests: mock compiled graph yielding fake node patches; assert correct events fired.

7. **Wire into `AgentRuntime.run_graph_request()`** — accept optional `event_sink` parameter;
   switch from `compiled_graph.invoke()` to `EventStreamAdapter.run_with_streaming()`.

8. **Wire into `DemoAgent.execute_graph_command()`** — construct sink from CLI flags;
   remove or demote `ProgressIndicator`.

9. **Update `demo_agent_cli.py`** — pass `--quiet` / `--json` flags into sink construction.

10. **Run full test suite** — no Ollama required; all LLM-dependent tests use existing mocks.

---

## 11. Files to Create or Modify

| File | Action | What changes |
|---|---|---|
| `src/application/agent_runtime/streaming/__init__.py` | Create | Package marker |
| `src/application/agent_runtime/streaming/live_agent_event.py` | Create | `LiveAgentEvent` dataclass + `LiveAgentEventType` enum |
| `src/application/agent_runtime/streaming/live_event_sink.py` | Create | `LiveEventSink` protocol + `NullEventSink` |
| `src/application/agent_runtime/streaming/console_event_sink.py` | Create | `ConsoleLiveEventSink` — ANSI live output |
| `src/application/agent_runtime/streaming/event_stream_adapter.py` | Create | `EventStreamAdapter` — LangGraph stream → sink bridge |
| `src/application/agent_runtime/progress/thinking_animation.py:63-65` | Edit | Stop reprinting last stage; print each stage once |
| `src/application/agent_runtime/react_loop/react_trace_builder.py:131-169` | Edit | Accept `user_input`; use `answer_intent` for specific thought summaries |
| `src/application/agent_runtime/presenters/console_presenter.py:76` | Edit | Prefer `response_text` over stale `data["answer"]` |
| `src/application/agent_runtime/demo_agent_runtime.py` | Edit | `run_graph_request()` accepts optional `event_sink`; uses adapter when sink provided |
| `src/application/agent_runtime/demo_agent.py` | Edit | `execute_graph_command()` constructs sink; passes to runtime |
| `scripts/demo_agent_cli.py` | Edit | Thread `--quiet` / `--json` into sink construction |
| `tests/unit/application/agent_runtime/streaming/` | Create | Unit tests for all streaming components |
| `tests/unit/application/agent_runtime/test_live_react_streaming.py` | Create | Integration: FAIL visible, PASS shows answer, no duplicate stages |
| `tests/unit/application/agent_runtime/test_reference_lookup_routing.py` | Create | Routing + thought summary for identifier-lookup queries |
| `tests/unit/cli_scripts/test_demo_agent_cli_live_output.py` | Create | CLI: no duplicate stage lines, FAIL message visible |

---

## 12. Test Scenarios Required

| Scenario | File | What to assert |
|---|---|---|
| FAIL message visible to user | `test_live_react_streaming.py` | `response_text` appears; `data["answer"]` does not |
| PASS shows LLM answer | `test_live_react_streaming.py` | `data["answer"]` appears when response_text matches |
| Stage printed exactly once | `test_demo_agent_cli_live_output.py` | "Finalizing response..." appears ≤1 time in stdout |
| Identifier-lookup thought | `test_reference_lookup_routing.py` | Thought contains "identifier" for manufacturer/supplier query |
| NullEventSink no output | `streaming/test_null_sink.py` | No stdout for any event type |
| ConsoleLiveEventSink order | `streaming/test_console_sink.py` | Events printed in emission order |
| EventStreamAdapter maps nodes | `streaming/test_event_stream_adapter.py` | `route_request` → `UNDERSTAND_REQUEST` event |
| Adapter returns final state | `streaming/test_event_stream_adapter.py` | Final state is assembled from all patches |
| Deep research events emitted | `test_live_react_streaming.py` | `PLAN_STARTED`, `ACTION_STARTED`, `RUN_COMPLETED` in order |
| Quiet mode suppresses output | `test_demo_agent_cli_live_output.py` | No stage or event output when `--quiet` |

---

## 12.5 Implementation Status

**Completed — 2026-07-01**

| Step | File(s) | Status |
|---|---|---|
| Fix ThinkingAnimation spam | `thinking_animation.py:53-65` | Done |
| Fix reflection FAIL suppressed | `console_presenter.py:76` | Done |
| Intent-specific thought summaries | `react_trace_builder.py:131-169` | Done |
| Create streaming package | `src/application/agent_runtime/streaming/` | Done |
| Wire `EventStreamAdapter` into graph | `document_agent_graph.py:_invoke()`, `run()` | Done |
| Add `event_sink` to `AgentRuntime` | `demo_agent_runtime.py:run_graph_request()` | Done |
| Replace `ProgressIndicator` in `DemoAgent` | `demo_agent.py:execute_graph_command()` | Done |
| Remove `ProgressIndicator` from CLI construction | `scripts/demo_agent_cli.py` | Done |
| Remove dead `_progress_stages()` function | `demo_agent.py` | Done |
| Unit tests — streaming package | `tests/unit/.../streaming/` (4 files) | Done |
| Integration tests — FAIL visibility, events | `test_live_react_streaming.py` | Done |
| Tests — intent-specific routing | `test_reference_lookup_routing.py` | Done |
| Tests — animation no-repeat | `test_demo_agent_cli_live_output.py` | Done |

**Test results (initial):** 149 agent runtime + CLI tests pass.

---

## 12.6 Presentation Upgrade — 2026-07-01

Upgraded `ConsoleLiveEventSink` from generic developer labels to a clean numbered agent loop format. Upgraded `EventStreamAdapter` payload extraction to include rich observation data. Updated `ReactPresenter` title.

| Change | File(s) | Detail |
|---|---|---|
| `ConsoleLiveEventSink` stateful step counter | `console_event_sink.py` | `[N] Understand / Retrieve / Plan / Reflect / Guardrail` with indented details |
| Silent events | `console_event_sink.py` | `FINAL_STARTED`, `FINAL_COMPLETED`, `RUN_COMPLETED`, `STRATEGY_*`, `PLAN_STARTED`, `ACTION_STARTED`, `REFLECTION_STARTED` produce no output |
| Rich `ACTION_COMPLETED` payload | `event_stream_adapter.py` | `description` with page numbers from `context_chunks` |
| Rich `PLAN_COMPLETED` payload | `event_stream_adapter.py` | `task_titles` list, not just `task_count` |
| Rich `REFLECTION_COMPLETED` payload | `event_stream_adapter.py` | `reason` from `reflection_result.decision.reason` |
| `OBSERVATION` payload | `event_stream_adapter.py` | `detail` from synthesis/summary patch keys |
| `ReactPresenter` title | `react_presenter.py` | "Agent Trace" → "Agent Loop" |
| New test file | `test_agent_loop_style.py` | 14 tests covering full sequence, silence rules, step numbering, ReactPresenter title |
| Updated tests | `test_console_event_sink.py` | Rewritten to match new format (17 tests) |
| Updated tests | `test_event_stream_adapter.py` | 5 new tests for richer payloads |
| Updated tests | `test_live_react_streaming.py` | 2 tests updated for new format |

**Test results (final):** 175 agent runtime + CLI tests pass. No regressions.

---

## 13. Acceptance Criteria

- [x] "Finalizing response..." appears at most once per query.
- [x] For deep-research queries, distinct stage names appear in sequence, each exactly once.
- [x] ReAct trace steps appear on stdout as the graph progresses — not only after completion.
- [x] A query for "manufacturer and supplier page references" produces a thought step that
      mentions identifiers or reference lookup — not the generic "retrieve grounded context" boilerplate.
- [x] A reflection FAIL results in the safe failure message reaching the user; the LLM-generated
      answer is not shown.
- [x] Agent loop output is structured: `[N] Understand → [N] Retrieve → Observation → [N] Reflect → Final Answer`.
- [x] FINAL_STARTED / FINAL_COMPLETED are silent — presenter owns "Final Answer" section; no duplication.
- [x] All tests pass without Ollama; all LLM paths use mocks.
- [x] No new facade or backwards-compatibility module introduced.
